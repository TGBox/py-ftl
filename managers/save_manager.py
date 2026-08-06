import hashlib
import json
import os
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
from classes.Room import Room
from classes.ShieldSystem import ShieldSystem
from classes.ShipModel import SHIP_BLUEPRINTS
from classes.Weapon import Weapon
from settings import STATE_GAME_OVER, STATE_MAIN_MENU, STATE_MAP, STATE_VICTORY

KEY_SALT = b"FTL_SECRET_SALT_2026_VERSION_1.0"
PASSPHRASE = b"PyGame_FTL_Encryption_Seed"


class SaveManager:

    @staticmethod
    def get_key() -> bytes:
        return PBKDF2(PASSPHRASE, KEY_SALT, dkLen=32, count=1000)

    @classmethod
    def has_savegame(cls, filepath: str = "savegame.dat") -> bool:
        return os.path.exists(filepath) and os.path.getsize(filepath) > 0

    @classmethod
    def save_game(cls, data: GameData, filepath: str = "savegame.dat") -> bool:
        try:
            # Map-Knoten serialisieren
            node_schemas = []
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
                )
                for r in data.player.ship.rooms
            ]

            # Waffen serialisieren
            weapon_schemas = [
                WeaponSaveSchema(
                    name=w.name,
                    charge_time=w.charge_time,
                    w_type=w.w_type,
                    shield_pierce=w.shield_pierce,
                    damage=w.damage,
                    ammo_cost=w.ammo_cost,
                )
                for w in data.player.weapons
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
                )
                for c in data.player.crew
            ]

            schema = SavegameSchema(
                schema_version=2,
                current_sector=data.world.star_map.sector,
                rebel_fleet_x=data.world.star_map.rebel_fleet_x,
                sector_type=data.world.star_map.sector_type,
                current_state=data.current_state,
                current_node_id=current_node_id,
                nodes=node_schemas,
                player_scrap=data.player.scrap,
                player_fuel=data.player.fuel,
                player_missiles=data.player.missiles,
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
            )
            json_str = schema.model_dump_json()

            # SHA-256 Integrity Hash (SRS Kap. 8)
            sha256_hash = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
            payload = json.dumps({"hash": sha256_hash, "data": json_str})

            # AES-256-CFB Encryption (SRS Kap. 8)
            key = cls.get_key()
            cipher = AES.new(key, AES.MODE_CFB)
            iv = cipher.iv
            ciphertext = cipher.encrypt(payload.encode("utf-8"))

            with open(filepath, "wb") as f:
                f.write(iv + ciphertext)

            print(f"Spielstand erfolgreich gespeichert in {filepath}!")
            return True
        except Exception as e:
            print(f"Fehler beim Speichern des Spielstands: {e}")
            return False

    @classmethod
    def load_game(cls, data: GameData, filepath: str = "savegame.dat") -> bool:
        if not os.path.exists(filepath):
            print(f"Kein Speicherstand unter {filepath} gefunden!")
            return False

        try:
            with open(filepath, "rb") as f:
                file_bytes = f.read()

            iv = file_bytes[:16]
            ciphertext = file_bytes[16:]
            key = cls.get_key()
            cipher = AES.new(key, AES.MODE_CFB, iv=iv)
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
            data.player.scrap = schema.player_scrap
            data.player.fuel = schema.player_fuel
            data.player.missiles = schema.player_missiles
            data.player.unlocked_ships = schema.unlocked_ships

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
                    data.player.crew.append(c)

            # Transient states zurücksetzen
            data.player.projectiles.clear()
            data.combat.weapon_targets.clear()
            data.combat.is_targeting = False
            data.combat.target_weapon_idx = None
            data.paused = False

            target_state = schema.current_state if schema.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY) else STATE_MAP
            data.current_state = target_state

            print(f"Spielstand erfolgreich geladen aus {filepath}!")
            return True

        except Exception as e:
            print(f"Fehler beim Laden des Spielstands: {e}")
            return False
