from typing import TYPE_CHECKING


import hashlib
import json
import os
from typing import Any
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

from classes.Crew import Crew
from classes.DataModels import (
    CrewSaveSchema,
    NodeSaveSchema,
    RoomSaveSchema,
    SavegameSchema,
    WeaponSaveSchema,
)
from classes.GameData import GameData
from classes.Node import Node
from classes.Reactor import Reactor
from classes.ShieldSystem import ShieldSystem
from classes.ShipModel import SHIP_BLUEPRINTS
from classes.Weapon import Weapon
from settings import STATE_GAME_OVER, STATE_MAIN_MENU, STATE_MAP, STATE_VICTORY

if TYPE_CHECKING:
    from game import Game
    
KEY_SALT = b"FTL_SECRET_SALT_2026_VERSION_1.0"
PASSPHRASE = b"PyGame_FTL_Encryption_Seed"


class SaveManager:
    def __init__(self) -> None:
        self.game: "Game | None" = None

    @staticmethod
    def get_key() -> bytes:
        return PBKDF2(str(PASSPHRASE), KEY_SALT, dkLen=32, count=1000)

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
        # Migrate legacy save file to slot 1 if needed
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
    def get_slot_info(cls, slot: int = 1) -> dict[str, Any] | None:
        path = cls.get_slot_filepath(slot)
        if not cls.has_savegame(slot, path):
            return None
        try:
            with open(path, "rb") as f:
                file_bytes = f.read()

            iv = file_bytes[:16]
            ciphertext = file_bytes[16:]
            key = cls.get_key()
            cipher = AES.new(key, AES.MODE_CFB, iv=iv)  # type: ignore
            decrypted_text = cipher.decrypt(ciphertext).decode("utf-8")

            payload = json.loads(decrypted_text)
            json_str = payload["data"]
            schema = SavegameSchema.model_validate_json(json_str)

            import datetime
            mtime_sec = os.path.getmtime(path)
            time_str = datetime.datetime.fromtimestamp(mtime_sec).strftime("%d.%m.%Y %H:%M")

            return {
                "slot": slot,
                "ship_name": schema.ship_name,
                "sector": schema.current_sector,
                "sector_type": schema.sector_type,
                "scrap": schema.player_scrap,
                "hp": f"{schema.ship_hp}/{schema.max_hp}",
                "time_str": time_str,
            }
        except Exception:
            return None

    @classmethod
    def save_game(cls, data: GameData, game: "Game", slot: int | str = 1, filepath: str | None = None) -> bool:
        if isinstance(slot, str) and ("/" in slot or "\\" in slot or slot.endswith(".dat")):
            path = slot
            _ = 1
        elif filepath is not None:
            path = filepath
            _ = slot if isinstance(slot, int) else 1
        else:
            path = cls.get_slot_filepath(slot)
            _ = slot if isinstance(slot, int) else 1

        try:
            # Map-Knoten serialisieren
            node_schemas: list[NodeSaveSchema] = []
            for n in data.world.star_map.nodes:
                conn_ids = [c.id for c in n.connections]
                node_schemas.append(
                    NodeSaveSchema(
                        id=n.id,
                        x=n.x,
                        y=n.y,
                        event_type=n.event_type,
                        visited=n.visited,
                        connection_ids=conn_ids,
                    )
                )

            current_node_id = (
                data.world.star_map.current_node.id
                if data.world.star_map.current_node
                else 0
            )

            # Räume serialisieren
            room_schemas = [
                RoomSaveSchema(
                    name=r.name,
                    health=r.health,
                    max_health=r.max_health,
                    current_power=r.current_power,
                    max_power=r.max_power,
                    oxygen=r.oxygen,
                    has_breach=getattr(r, "has_breach", False),
                    was_destroyed=getattr(r, "was_destroyed", False),
                )
                for r in data.player.ship.rooms
            ]

            # Waffen serialisieren
            assert data.player.weapons is not None
            weapon_schemas = [
                WeaponSaveSchema(
                    name=w.name,
                    charge_time=w.charge_time,
                    w_type=w.w_type,
                    shield_pierce=w.shield_pierce,
                    damage=w.damage,
                    ammo_cost=w.ammo_cost,
                    level=getattr(w, "level", 1),
                    subtype=getattr(w, "subtype", "STANDARD"),
                    fire_chance=getattr(w, "fire_chance", 0.0),
                    breach_chance=getattr(w, "breach_chance", 0.0),
                    stun_duration=getattr(w, "stun_duration", 0.0),
                    crew_damage=getattr(w, "crew_damage", 0.0),
                    max_range=getattr(w, "max_range", None),
                )
                for w in data.player.weapons if w is not None  # <- "if w is not None" hinzufügen
            ]

            # Crew serialisieren
            crew_schemas = [
                CrewSaveSchema(
                    name=c.name,
                    species=c.species,
                    hp=c.hp,
                    max_hp=c.max_hp,
                    trait=getattr(c, "trait", "Sprinter"),
                    x=c.x,
                    y=c.y,
                    skill_repair=getattr(c, "skill_repair", 0),
                    skill_combat=getattr(c, "skill_combat", 0),
                    skill_piloting=getattr(c, "skill_piloting", 0),
                    skill_fitness=getattr(c, "skill_fitness", 0),
                )
                for c in data.player.crew
            ]

            schema = SavegameSchema(
                schema_version=2,
                auto_save_enabled=getattr(data, "auto_save_enabled", False),
                current_sector=data.world.star_map.sector,
                rebel_fleet_x=data.world.star_map.rebel_fleet_x,
                sector_type=data.world.star_map.sector_type,
                current_state=data.current_state,
                current_node_id=current_node_id,
                nodes=node_schemas,
                player_scrap=data.player.scrap,
                player_fuel=data.player.fuel,
                player_missiles=data.player.missiles,
                player_drone_parts=getattr(data.player, "drone_parts", 5),
                ship_name=data.player.ship.name,
                ship_hp=int(data.player.ship.hp),
                max_hp=int(data.player.ship.max_hp),
                reactor_total_power=data.player.reactor.total_power,
                reactor_available_power=data.player.reactor.available_power,
                shield_max_layers=data.player.shield.max_layers,
                rooms=room_schemas,
                weapons=weapon_schemas,
                crew=crew_schemas,
                unlocked_ships=getattr(data.player, "unlocked_ships", ["Kestrel"]),
                disqualified_from_unlocks=getattr(data.player, "disqualified_from_unlocks", False),
            )
            json_str = schema.model_dump_json()

            # SHA-256 Integrity Hash (SRS Kap. 8)
            sha256_hash = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
            payload = json.dumps({"hash": sha256_hash, "data": json_str})

            # AES-256-CFB Encryption (SRS Kap. 8)
            key = cls.get_key()
            cipher: Any = AES.new(key, AES.MODE_CFB) # type: ignore
            iv = cipher.iv
            ciphertext = cipher.encrypt(payload.encode("utf-8"))

            with open(path, "wb") as f:
                f.write(iv + ciphertext)

            from managers.logger_manager import log_debug
            log_debug("SAVE", f"Spielstand erfolgreich in Datei/Slot '{slot}' gespeichert.")

            game.save_notification_msg = f"SPIELSTAND GESPEICHERT (SLOT {slot})"
            game.save_notification_timer = 3.0
            data.combat.msg = f"💾 SPIELSTAND ERFOLGREICH GESPEICHERT (SLOT {slot})!"
            data.combat.msg_timer = 3.0
            data.active_save_slot = int(slot) if str(slot).isdigit() else 1

            print(f"Spielstand erfolgreich gespeichert in {path} (Slot {slot})!")
            return True
        except Exception as e:
            print(f"Fehler beim Speichern des Spielstands: {e}")
            return False

    @classmethod
    def load_game(cls, data: GameData, slot: int | str = 1, filepath: str | None = None) -> bool:
        if isinstance(slot, str) and ("/" in slot or "\\" in slot or slot.endswith(".dat")):
            path = slot
            _ = 1
        elif filepath is not None:
            path = filepath
            _ = slot if isinstance(slot, int) else 1
        else:
            path = cls.get_slot_filepath(slot)
            _ = slot if isinstance(slot, int) else 1

        if not os.path.exists(path):
            print(f"Kein Speicherstand unter {path} gefunden!")
            return False

        try:
            with open(path, "rb") as f:
                file_bytes = f.read()

            iv = file_bytes[:16]
            ciphertext = file_bytes[16:]
            key = cls.get_key()
            cipher: Any = AES.new(key, AES.MODE_CFB, iv=iv)  # type: ignore
            decrypted_text = cipher.decrypt(ciphertext).decode("utf-8")

            payload = json.loads(decrypted_text)
            stored_hash = payload.get("hash")
            json_str = payload.get("data")

            # SHA-256 Verifizierung
            actual_hash = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
            if stored_hash != actual_hash:
                print("KORRUMPIERTER SPEICHERSTAND! Hash-Verifizierung fehlgeschlagen.")
                return False

            schema = SavegameSchema.model_validate_json(json_str)

            # 1. Sternenkarte wiederherstellen
            if schema.nodes:
                data.world.star_map.nodes.clear()
                node_map: dict[int, Node] = {}
                for ns in schema.nodes:
                    n = Node(ns.id, ns.x, ns.y, ns.event_type)
                    n.visited = ns.visited
                    data.world.star_map.nodes.append(n)
                    node_map[ns.id] = n

                # Verbindungen wiederherstellen
                for ns in schema.nodes:
                    curr_node = node_map.get(ns.id)
                    if curr_node:
                        for cid in ns.connection_ids:
                            target = node_map.get(cid)
                            if target and target not in curr_node.connections:
                                curr_node.connections.append(target)

                data.world.star_map.current_node = node_map.get(schema.current_node_id)
                data.world.star_map.rebel_fleet_x = schema.rebel_fleet_x
                data.world.star_map.sector_type = schema.sector_type

            data.world.star_map.sector = schema.current_sector

            # 2. Ressourcen & Spieler-Basiswerte
            data.auto_save_enabled = getattr(schema, "auto_save_enabled", False)
            data.player.scrap = schema.player_scrap
            data.player.fuel = schema.player_fuel
            data.player.missiles = schema.player_missiles
            data.player.drone_parts = getattr(schema, "player_drone_parts", 5)

            persistent_unlocks = cls.load_unlocks()
            saved_disqualified = getattr(schema, "disqualified_from_unlocks", False)

            # Qualifiziert nur, wenn das Schiff im aktuellen Profil freigeschaltet ist und das Savegame nicht disqualifiziert war
            ship_is_unlocked = (schema.ship_name in persistent_unlocks)
            is_disqualified = saved_disqualified or (not ship_is_unlocked)

            data.player.unlocked_ships = persistent_unlocks
            data.player.disqualified_from_unlocks = is_disqualified

            if is_disqualified:
                data.combat.msg = "⚠️ HINWEIS: UNLOCKS & ERRUNGENSCHAFTEN DEAKTIVIERT!"
                data.combat.msg_timer = 5.0

            # 3. Raumschiff & Räume wiederherstellen
            import copy
            blueprint = SHIP_BLUEPRINTS.get(schema.ship_name, SHIP_BLUEPRINTS["Kestrel"])
            data.player.ship = copy.deepcopy(blueprint)
            data.player.ship.name = schema.ship_name
            data.player.ship.hp = schema.ship_hp
            data.player.ship.max_hp = schema.max_hp

            if schema.rooms and len(schema.rooms) == len(data.player.ship.rooms):
                for idx, r_schema in enumerate(schema.rooms):
                    r = data.player.ship.rooms[idx]
                    r.health = r_schema.health
                    r.max_health = r_schema.max_health
                    r.current_power = r_schema.current_power
                    r.max_power = r_schema.max_power
                    r.oxygen = r_schema.oxygen
                    r.has_breach = r_schema.has_breach
                    r.was_destroyed = getattr(r_schema, "was_destroyed", False)

            # 4. Reaktor & Schild wiederherstellen
            data.player.reactor = Reactor(total_power=schema.reactor_total_power)
            data.player.reactor.available_power = schema.reactor_available_power
            data.player.shield = ShieldSystem()

            # 5. Waffen wiederherstellen
            if schema.weapons:
                data.player.weapons = [
                    Weapon(
                        ws.name,
                        charge_time=ws.charge_time,
                        w_type=ws.w_type,
                        damage=ws.damage,
                        ammo_cost=ws.ammo_cost,
                        shield_pierce=ws.shield_pierce,
                        level=getattr(ws, "level", 1),
                        subtype=getattr(ws, "subtype", "STANDARD"),
                        fire_chance=getattr(ws, "fire_chance", 0.0),
                        breach_chance=getattr(ws, "breach_chance", 0.0),
                        stun_duration=getattr(ws, "stun_duration", 0.0),
                        crew_damage=getattr(ws, "crew_damage", 0.0),
                        max_range=getattr(ws, "max_range", None),
                    )
                    for ws in schema.weapons
                ]

            # 6. Crew wiederherstellen
            if schema.crew:
                data.player.crew.clear()
                for cs in schema.crew:
                    c = Crew(cs.x, cs.y, name=cs.name, species=cs.species)
                    c.hp = cs.hp
                    c.max_hp = cs.max_hp
                    c.trait = cs.trait
                    c.skill_repair = getattr(cs, "skill_repair", 0)
                    c.skill_combat = getattr(cs, "skill_combat", 0)
                    c.skill_piloting = getattr(cs, "skill_piloting", 0)
                    c.skill_fitness = getattr(cs, "skill_fitness", 0)
                    # Skill-Boni neu anwenden
                    c.repair_multiplier *= (1.25 ** c.skill_repair)
                    c.melee_multiplier *= (1.30 ** c.skill_combat)
                    data.player.crew.append(c)

            # Transient states zurücksetzen
            data.player.projectiles.clear()
            data.combat.weapon_targets.clear()
            data.combat.is_targeting = False
            data.combat.target_weapon_idx = None
            data.paused = False

            target_state = schema.current_state if schema.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY) else STATE_MAP
            data.current_state = target_state
            data.show_slot_modal = False

            print(f"Spielstand erfolgreich geladen aus {path} (Slot {slot})!")
            return True

        except Exception as e:
            print(f"Fehler beim Laden des Spielstands: {e}")
            return False
