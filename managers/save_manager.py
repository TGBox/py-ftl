import copy
import datetime
import hashlib
import json
import os
import zlib
from typing import TYPE_CHECKING, Any

from classes.Crew import Crew
from classes.GameData import GameData
from classes.Node import Node
from classes.Reactor import Reactor
from classes.ShieldSystem import ShieldSystem
from classes.ShipModel import SHIP_BLUEPRINTS
from classes.Weapon import Weapon
from settings import STATE_GAME_OVER, STATE_MAIN_MENU, STATE_MAP, STATE_VICTORY

if TYPE_CHECKING:
    from game import Game


class SaveManager:
    def __init__(self) -> None:
        self.game: "Game | None" = None

    @classmethod
    def load_unlocks(cls, filepath: str = "data/unlocks.json") -> list[str]:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    ships = data.get("unlocked_ships", ["Kestrel"])
                    if "Kestrel" not in ships:
                        ships.insert(0, "Kestrel")
                    return ships
            except Exception:
                pass
        return ["Kestrel"]

    @classmethod
    def save_unlocks(cls, unlocked_ships: list[str], filepath: str = "data/unlocks.json") -> bool:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"unlocked_ships": unlocked_ships}, f, indent=2)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Unlocks: {e}")
            return False

    @classmethod
    def get_slot_filepath(cls, slot: int | str = 1) -> str:
        if isinstance(slot, str) and ("/" in slot or "\\" in slot or slot.endswith(".dat")):
            return slot
        os.makedirs("data", exist_ok=True)
        legacy_path = "data/savegame.dat"
        target_path = f"data/savegame_slot_{slot}.dat"
        if slot == 1 and not os.path.exists(target_path) and os.path.exists(legacy_path):
            try:
                os.replace(legacy_path, target_path)
            except Exception:
                pass
        return target_path

    @classmethod
    def has_savegame(cls, slot: int | str = 1, filepath: str | None = None) -> bool:
        if isinstance(slot, str) and ("/" in slot or "\\" in slot or slot.endswith(".dat")):
            path = slot
        else:
            path = filepath or cls.get_slot_filepath(slot)
        return os.path.exists(path) and os.path.getsize(path) > 0

    @classmethod
    def has_any_savegame(cls) -> bool:
        return any(cls.has_savegame(s) for s in (1, 2, 3, 4))

    @classmethod
    def save_emergency_game(cls, data: GameData, game: "Game") -> bool:
        """Speichert einen Notfall-Backup-Spielstand explizit in Slot 4."""
        return cls.save_game(data, game, slot=4)

    @classmethod
    def _read_save_payload(cls, path: str) -> dict[str, Any] | None:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return None
        with open(path, "rb") as f:
            file_bytes = f.read()

        payload = None
        # 1. Try compressed JSON
        try:
            decompressed = zlib.decompress(file_bytes)
            payload = json.loads(decompressed.decode("utf-8"))
        except Exception:
            pass

        # 2. Try legacy AES-256-CFB if pycryptodome happens to be available
        if payload is None:
            try:
                from Crypto.Cipher import AES
                from Crypto.Protocol.KDF import PBKDF2
                key = PBKDF2(str(b"PyGame_FTL_Encryption_Seed"), b"FTL_SECRET_SALT_2026_VERSION_1.0", dkLen=32, count=1000)
                iv = file_bytes[:16]
                ciphertext = file_bytes[16:]
                cipher = AES.new(key, AES.MODE_CFB, iv=iv)
                decrypted_text = cipher.decrypt(ciphertext).decode("utf-8")
                payload = json.loads(decrypted_text)
            except Exception:
                return None

        if not isinstance(payload, dict):
            return None

        stored_hash = payload.get("hash")
        json_str = payload.get("data")
        if not json_str:
            return None

        actual_hash = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
        if stored_hash != actual_hash:
            return None

        return json.loads(json_str)

    @classmethod
    def get_slot_info(cls, slot: int = 1) -> dict[str, Any] | None:
        path = cls.get_slot_filepath(slot)
        if not cls.has_savegame(slot, path):
            return None
        try:
            save_dict = cls._read_save_payload(path)
            if not save_dict:
                return None

            mtime_sec = os.path.getmtime(path)
            time_str = datetime.datetime.fromtimestamp(mtime_sec).strftime("%d.%m.%Y %H:%M")

            return {
                "slot": slot,
                "ship_name": save_dict.get("ship_name", "Kestrel"),
                "sector": save_dict.get("current_sector", 1),
                "sector_type": save_dict.get("sector_type", "Zivil"),
                "scrap": save_dict.get("player_scrap", 0),
                "hp": f"{save_dict.get('ship_hp', 15)}/{save_dict.get('max_hp', 15)}",
                "time_str": time_str,
            }
        except Exception:
            return None

    @classmethod
    def save_game(cls, data: GameData, game: "Game", slot: int | str = 1, filepath: str | None = None) -> bool:
        if isinstance(slot, str) and ("/" in slot or "\\" in slot or slot.endswith(".dat")):
            path = slot
        elif filepath is not None:
            path = filepath
        else:
            path = cls.get_slot_filepath(slot)

        try:
            nodes_data = [
                {
                    "id": n.id,
                    "x": n.x,
                    "y": n.y,
                    "event_type": n.event_type if isinstance(n.event_type, str) else n.event_type.value,
                    "visited": n.visited,
                    "connection_ids": [c.id for c in n.connections],
                }
                for n in data.world.star_map.nodes
            ]
            current_node_id = (
                data.world.star_map.current_node.id
                if data.world.star_map.current_node
                else 0
            )

            rooms_data = [
                {
                    "name": r.name,
                    "health": r.health,
                    "max_health": r.max_health,
                    "current_power": r.current_power,
                    "max_power": r.max_power,
                    "oxygen": r.oxygen,
                    "has_breach": getattr(r, "has_breach", False),
                    "was_destroyed": getattr(r, "was_destroyed", False),
                }
                for r in data.player.ship.rooms
            ]

            weapons_data = [
                {
                    "name": w.name,
                    "charge_time": w.charge_time,
                    "w_type": w.w_type if isinstance(w.w_type, str) else w.w_type.value,
                    "shield_pierce": w.shield_pierce,
                    "damage": w.damage,
                    "ammo_cost": w.ammo_cost,
                    "level": getattr(w, "level", 1),
                    "subtype": w.subtype if isinstance(w.subtype, str) else w.subtype.value,
                    "fire_chance": getattr(w, "fire_chance", 0.0),
                    "breach_chance": getattr(w, "breach_chance", 0.0),
                    "stun_duration": getattr(w, "stun_duration", 0.0),
                    "crew_damage": getattr(w, "crew_damage", 0.0),
                    "max_range": getattr(w, "max_range", None),
                }
                for w in (data.player.weapons or []) if w is not None
            ]

            crew_data = [
                {
                    "name": c.name,
                    "species": c.species,
                    "hp": c.hp,
                    "max_hp": c.max_hp,
                    "trait": getattr(c, "trait", "Sprinter"),
                    "x": c.x,
                    "y": c.y,
                    "skill_repair": getattr(c, "skill_repair", 0),
                    "skill_combat": getattr(c, "skill_combat", 0),
                    "skill_piloting": getattr(c, "skill_piloting", 0),
                    "skill_fitness": getattr(c, "skill_fitness", 0),
                }
                for c in data.player.crew
            ]

            save_dict = {
                "schema_version": 2,
                "auto_save_enabled": getattr(data, "auto_save_enabled", False),
                "current_sector": data.world.star_map.sector,
                "rebel_fleet_x": data.world.star_map.rebel_fleet_x,
                "sector_type": data.world.star_map.sector_type,
                "current_state": data.current_state,
                "current_node_id": current_node_id,
                "nodes": nodes_data,
                "player_scrap": data.player.scrap,
                "player_fuel": data.player.fuel,
                "player_missiles": data.player.missiles,
                "player_drone_parts": getattr(data.player, "drone_parts", 5),
                "ship_name": data.player.ship.name,
                "ship_hp": int(data.player.ship.hp),
                "max_hp": int(data.player.ship.max_hp),
                "reactor_total_power": data.player.reactor.total_power,
                "reactor_available_power": data.player.reactor.available_power,
                "shield_max_layers": data.player.shield.max_layers,
                "rooms": rooms_data,
                "weapons": weapons_data,
                "crew": crew_data,
                "unlocked_ships": getattr(data.player, "unlocked_ships", ["Kestrel"]),
                "disqualified_from_unlocks": getattr(data.player, "disqualified_from_unlocks", False),
            }

            json_str = json.dumps(save_dict)
            sha256_hash = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
            payload = json.dumps({"hash": sha256_hash, "data": json_str}).encode("utf-8")
            compressed = zlib.compress(payload)

            with open(path, "wb") as f:
                f.write(compressed)

            from managers.logger_manager import log_debug
            log_debug("SAVE", f"Spielstand erfolgreich in Datei/Slot '{slot}' gespeichert.")

            game.save_notification_msg = f"SPIELSTAND GESPEICHERT (SLOT {slot})"
            game.save_notification_timer = 3.0
            data.combat.msg = f"💾 SPIELSTAND ERFOLGREICH GESPEICHERT (SLOT {slot})!"
            data.combat.msg_timer = 3.0
            data.active_save_slot = int(slot) if str(slot).isdigit() else 1

            return True
        except Exception as e:
            print(f"Fehler beim Speichern des Spielstands: {e}")
            return False

    @classmethod
    def load_game(cls, data: GameData, slot: int | str = 1, filepath: str | None = None) -> bool:
        if isinstance(slot, str) and ("/" in slot or "\\" in slot or slot.endswith(".dat")):
            path = slot
        elif filepath is not None:
            path = filepath
        else:
            path = cls.get_slot_filepath(slot)

        if not os.path.exists(path):
            return False

        try:
            save_dict = cls._read_save_payload(path)
            if not save_dict:
                return False

            # 1. Sternenkarte wiederherstellen
            nodes_data = save_dict.get("nodes", [])
            if nodes_data:
                data.world.star_map.nodes.clear()
                node_map: dict[int, Node] = {}
                for ns in nodes_data:
                    n = Node(ns["id"], ns["x"], ns["y"], ns["event_type"])
                    n.visited = ns.get("visited", False)
                    data.world.star_map.nodes.append(n)
                    node_map[ns["id"]] = n

                for ns in nodes_data:
                    curr_node = node_map.get(ns["id"])
                    if curr_node:
                        for cid in ns.get("connection_ids", []):
                            target = node_map.get(cid)
                            if target and target not in curr_node.connections:
                                curr_node.connections.append(target)

                data.world.star_map.current_node = node_map.get(save_dict.get("current_node_id", 0))
                data.world.star_map.rebel_fleet_x = float(save_dict.get("rebel_fleet_x", 30.0))
                data.world.star_map.sector_type = save_dict.get("sector_type", "Zivil")

            data.world.star_map.sector = int(save_dict.get("current_sector", 1))

            # 2. Ressourcen & Spieler-Basiswerte
            data.auto_save_enabled = bool(save_dict.get("auto_save_enabled", False))
            data.player.scrap = int(save_dict.get("player_scrap", 20))
            data.player.fuel = int(save_dict.get("player_fuel", 6))
            data.player.missiles = int(save_dict.get("player_missiles", 6))
            data.player.drone_parts = int(save_dict.get("player_drone_parts", 5))

            persistent_unlocks = cls.load_unlocks()
            saved_disqualified = bool(save_dict.get("disqualified_from_unlocks", False))
            ship_name = save_dict.get("ship_name", "Kestrel")

            ship_is_unlocked = (ship_name in persistent_unlocks)
            is_disqualified = saved_disqualified or (not ship_is_unlocked)

            data.player.unlocked_ships = persistent_unlocks
            data.player.disqualified_from_unlocks = is_disqualified

            if is_disqualified:
                data.combat.msg = "⚠️ HINWEIS: UNLOCKS & ERRUNGENSCHAFTEN DEAKTIVIERT!"
                data.combat.msg_timer = 5.0

            # 3. Raumschiff & Räume wiederherstellen
            blueprint = SHIP_BLUEPRINTS.get(ship_name, SHIP_BLUEPRINTS["Kestrel"])
            data.player.ship = copy.deepcopy(blueprint)
            data.player.ship.name = ship_name
            data.player.ship.hp = int(save_dict.get("ship_hp", 15))
            data.player.ship.max_hp = int(save_dict.get("max_hp", 15))

            rooms_data = save_dict.get("rooms", [])
            if rooms_data and len(rooms_data) == len(data.player.ship.rooms):
                for idx, r_dict in enumerate(rooms_data):
                    r = data.player.ship.rooms[idx]
                    r.health = float(r_dict.get("health", 100.0))
                    r.max_health = float(r_dict.get("max_health", 100.0))
                    r.current_power = int(r_dict.get("current_power", 0))
                    r.max_power = int(r_dict.get("max_power", 1))
                    r.oxygen = float(r_dict.get("oxygen", 100.0))
                    r.has_breach = bool(r_dict.get("has_breach", False))
                    r.was_destroyed = bool(r_dict.get("was_destroyed", False))

            # 4. Reaktor & Schild wiederherstellen
            data.player.reactor = Reactor(total_power=int(save_dict.get("reactor_total_power", 6)))
            data.player.reactor.available_power = int(save_dict.get("reactor_available_power", 6))
            data.player.shield = ShieldSystem()

            # 5. Waffen wiederherstellen
            weapons_data = save_dict.get("weapons", [])
            if weapons_data:
                data.player.weapons = [
                    Weapon(
                        ws["name"],
                        charge_time=float(ws.get("charge_time", 3.0)),
                        w_type=ws.get("w_type", "LASER"),
                        damage=float(ws.get("damage", 35.0)),
                        ammo_cost=int(ws.get("ammo_cost", 0)),
                        shield_pierce=int(ws.get("shield_pierce", 0)),
                        level=int(ws.get("level", 1)),
                        subtype=ws.get("subtype", "STANDARD"),
                        fire_chance=float(ws.get("fire_chance", 0.0)),
                        breach_chance=float(ws.get("breach_chance", 0.0)),
                        stun_duration=float(ws.get("stun_duration", 0.0)),
                        crew_damage=float(ws.get("crew_damage", 0.0)),
                        max_range=ws.get("max_range"),
                    )
                    for ws in weapons_data
                ]

            # 6. Crew wiederherstellen
            crew_data = save_dict.get("crew", [])
            if crew_data:
                data.player.crew.clear()
                for cs in crew_data:
                    c = Crew(float(cs["x"]), float(cs["y"]), name=cs.get("name", "Crew"), species=cs.get("species", "Mensch"))
                    c.hp = float(cs.get("hp", 100.0))
                    c.max_hp = float(cs.get("max_hp", 100.0))
                    c.trait = cs.get("trait", "Sprinter")
                    c.skill_repair = int(cs.get("skill_repair", 0))
                    c.skill_combat = int(cs.get("skill_combat", 0))
                    c.skill_piloting = int(cs.get("skill_piloting", 0))
                    c.skill_fitness = int(cs.get("skill_fitness", 0))
                    c.repair_multiplier *= (1.25 ** c.skill_repair)
                    c.melee_multiplier *= (1.30 ** c.skill_combat)
                    data.player.crew.append(c)

            # Transient states zurücksetzen
            data.player.projectiles.clear()
            data.combat.weapon_targets.clear()
            data.combat.is_targeting = False
            data.combat.target_weapon_idx = None
            data.paused = False

            current_st = save_dict.get("current_state", STATE_MAP)
            target_state = current_st if current_st not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY) else STATE_MAP
            data.current_state = target_state
            data.show_slot_modal = False

            return True
        except Exception as e:
            print(f"Fehler beim Laden des Spielstands: {e}")
            return False
