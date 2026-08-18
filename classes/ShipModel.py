from typing import TYPE_CHECKING


from typing import Any

import pygame

from classes.Crew import Crew
from classes.Door import Door
from classes.Room import Room
from classes.Weapon import Weapon
from enums import ShipType

if TYPE_CHECKING:
    from classes.GameData import PlayerData


class ShipModel:
    def __init__(
        self,
        name: ShipType | str,
        max_hp: int,
        rooms: list[Room],
        is_enemy: bool = False,
        max_weapons: int = 3,
        max_crew: int = 4,
        weapon_slots: list[dict[str, int | tuple[int, int] | list[str] | None]] = [],
    ):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.rooms = rooms
        self.is_enemy = is_enemy
        self.max_weapons = max_weapons
        self.max_crew = max_crew
        self.weapon_slots: list[dict[Any, Any]] = weapon_slots or []
        self.doors: list[Door] = []
        self.generate_doors()
        if not self.weapon_slots:
            self.generate_default_weapon_slots()
            
    def __str__(self) -> str:
        """Methode um aus dem ShipModel Objekt einen wohlgeformten und von Menschen gut lesbaren String zu generieren.

        Returns:
            str: Die String Repräsentation des ShipModels.
        """
        s_str = (f"{"Gegnerisches " if self.is_enemy else "Spieler "}Schiff: \"{self.name}\" | "
                 f"Gesundheit: {self.hp} / {self.max_hp} | {len(self.rooms)} Räume | Maximale Crew: "
                 f"{self.max_crew} Mitglieder | Maximale Anzahl Waffen: {len(self.weapon_slots)} | {len(self.doors)} Türen")
        return s_str

    def generate_default_weapon_slots(self) -> None:
        self.weapon_slots = []
        if self.rooms:
            w_room = self.rooms[1] if len(self.rooms) > 1 else self.rooms[0]
            cx, cy = w_room.rect.centerx, w_room.rect.centery
            for i in range(self.max_weapons):
                offset_y = (i - (self.max_weapons - 1) / 2.0) * 35.0
                self.weapon_slots.append({
                    "slot_id": i + 1,
                    "pos": (int(cx), int(cy + offset_y)),
                    "allowed_types": None,
                })

    def swap_room_systems(self, r1: Room, r2: Room) -> None:
        if r1 not in self.rooms or r2 not in self.rooms or r1 == r2:
            return

        # System-Eigenschaften tauschen (Name, Power, Health, Breach, Fire)
        r1.name, r2.name = r2.name, r1.name
        r1.max_power, r2.max_power = r2.max_power, r1.max_power
        r1.current_power, r2.current_power = r2.current_power, r1.current_power
        r1.health, r2.health = r2.health, r1.health
        r1.max_health, r2.max_health = r2.max_health, r1.max_health
        r1.oxygen, r2.oxygen = r2.oxygen, r1.oxygen
        r1.has_breach, r2.has_breach = r2.has_breach, r1.has_breach
        r1.fire_level, r2.fire_level = r2.fire_level, r1.fire_level
        r1.ion_timer, r2.ion_timer = r2.ion_timer, r1.ion_timer

        # Waffenslot-Positionen an die neue Position des Waffenraums anpassen
        w_room = next((r for r in self.rooms if r.name == "Waffen"), None)
        if w_room:
            cx, cy = w_room.rect.centerx, w_room.rect.centery
            for i, slot in enumerate(self.weapon_slots):
                offset_y = (i - (len(self.weapon_slots) - 1) / 2.0) * 35.0
                slot["pos"] = (int(cx), int(cy + offset_y))

        # Türen & Luftschleusen neu berechnen
        self.generate_doors()

    def swap_weapon_slots(self, idx1: int, idx2: int, weapons_list: list) -> bool:
        # Optional: Prüfen, ob die Indizes im gültigen Bereich liegen
        if not (0 <= idx1 < len(self.weapon_slots) and 0 <= idx2 < len(self.weapon_slots)):
            return False

        # 1. Die Waffen in der übergebenen Inventarliste tauschen
        if 0 <= idx1 < len(weapons_list) and 0 <= idx2 < len(weapons_list):
            weapons_list[idx1], weapons_list[idx2] = weapons_list[idx2], weapons_list[idx1]
            
        # 2. Die Eigenschaften der Slots im Schiff tauschen
        self.weapon_slots[idx1], self.weapon_slots[idx2] = self.weapon_slots[idx2], self.weapon_slots[idx1]
        
        return True

    def generate_doors(self) -> None:
        self.doors.clear()
        # 1. Innentüren zwischen angrenzenden Räumen
        for i in range(len(self.rooms)):
            for j in range(i + 1, len(self.rooms)):
                r1 = self.rooms[i]
                r2 = self.rooms[j]
                rect1 = r1.rect
                rect2 = r2.rect

                if abs(rect1.right - rect2.left) <= 15 or abs(rect2.right - rect1.left) <= 15:
                    top = max(rect1.top, rect2.top)
                    bottom = min(rect1.bottom, rect2.bottom)
                    if bottom - top >= 20:
                        mid_y = (top + bottom) // 2
                        x = rect1.right if abs(rect1.right - rect2.left) <= 15 else rect2.right
                        self.doors.append(Door(r1, r2, (x - 3, mid_y - 12, 6, 24), is_airlock=False))

                elif abs(rect1.bottom - rect2.top) <= 15 or abs(rect2.bottom - rect1.top) <= 15:
                    left = max(rect1.left, rect2.left)
                    right = min(rect1.right, rect2.right)
                    if right - left >= 20:
                        mid_x = (left + right) // 2
                        y = rect1.bottom if abs(rect1.bottom - rect2.top) <= 15 else rect2.bottom
                        self.doors.append(Door(r1, r2, (mid_x - 12, y - 3, 24, 6), is_airlock=False))

        # 2. Äußere Luftschleusen (Airlocks nach außen ins Weltall)
        if not self.is_enemy and self.rooms:
            min_x_room = min(self.rooms, key=lambda r: r.rect.left)
            max_x_room = max(self.rooms, key=lambda r: r.rect.right)
            self.doors.append(Door(min_x_room, None, (min_x_room.rect.left - 4, min_x_room.rect.centery - 12, 6, 24), is_airlock=True))
            self.doors.append(Door(max_x_room, None, (max_x_room.rect.right - 2, max_x_room.rect.centery - 12, 6, 24), is_airlock=True))

    def update_doors(self, dt: float, crew_list: list[Crew] | None = None) -> None:
        for d in self.doors:
            d.update(dt)
            if d.opened_by_crew and not d.is_airlock:
                near = False
                if crew_list:
                    check_rect = d.rect.inflate(36, 36)
                    for c in crew_list:
                        if check_rect.collidepoint(int(c.x), int(c.y)):
                            near = True
                            break
                if not near:
                    d.is_open = False
                    d.opened_by_crew = False

    def draw_doors(self, surface: pygame.Surface, door_level: int = 1) -> None:
        for d in self.doors:
            d.draw(surface, door_level=door_level)

    def open_all_doors(self) -> None:
        for d in self.doors:
            if not d.is_airlock:
                d.is_open = True
                d.opened_by_crew = False

    def close_all_doors(self) -> None:
        for d in self.doors:
            d.is_open = False
            d.opened_by_crew = False

    def open_airlocks(self) -> None:
        for d in self.doors:
            if d.is_airlock:
                d.is_open = not d.is_open
                d.opened_by_crew = False


PLAYER_SHIP = ShipModel(ShipType.KESTREL, 15, [
    Room("Schild", (60, 245, 90, 90)),
    Room("Waffen", (160, 245, 90, 90)),
    Room("Brücke", (260, 245, 90, 90), max_power=2),
    Room("Medbay", (160, 145, 90, 90), max_power=2),
    Room("Teleporter", (260, 145, 90, 90), max_power=1),
    Room("Tarnung", (60, 145, 90, 90), max_power=2),
    Room("Sensoren", (360, 245, 90, 90), max_power=2),
    Room("Drohnen-Kontrolle", (360, 145, 90, 90), max_power=3),
], max_weapons=3, max_crew=4, weapon_slots=[
    {"slot_id": 1, "pos": (205, 230), "allowed_types": ["LASER", "BEAM", "MISSILE"]},
    {"slot_id": 2, "pos": (205, 350), "allowed_types": ["LASER", "MISSILE"]},
    {"slot_id": 3, "pos": (335, 290), "allowed_types": ["MISSILE", "BEAM"]},
])

CRUISER_SHIP = ShipModel("Kreuzer", 18, [
    Room("Schild", (50, 235, 85, 85)),
    Room("Waffen", (145, 235, 85, 85)),
    Room("Maschinen", (240, 235, 85, 85)),
    Room("Brücke", (335, 235, 85, 85), max_power=2),
    Room("Medbay", (145, 140, 85, 85), max_power=2),
], max_weapons=4, max_crew=6, weapon_slots=[
    {"slot_id": 1, "pos": (187, 220), "allowed_types": ["LASER", "BEAM", "MISSILE"]},
    {"slot_id": 2, "pos": (187, 335), "allowed_types": ["LASER", "BEAM"]},
    {"slot_id": 3, "pos": (282, 220), "allowed_types": ["MISSILE", "BEAM"]},
    {"slot_id": 4, "pos": (377, 290), "allowed_types": ["LASER", "MISSILE"]},
])

STEALTH_SHIP = ShipModel(ShipType.TARNSSCHIFF, 12, [
    Room("Tarnung", (70, 245, 80, 80)),
    Room("Waffen", (160, 245, 80, 80)),
    Room("Brücke", (250, 245, 80, 80), max_power=2),
    Room("Medbay", (160, 155, 80, 80), max_power=1),
], max_weapons=3, max_crew=3, weapon_slots=[
    {"slot_id": 1, "pos": (200, 230), "allowed_types": ["LASER", "BEAM"]},
    {"slot_id": 2, "pos": (200, 340), "allowed_types": ["BEAM", "LASER"]},
    {"slot_id": 3, "pos": (290, 285), "allowed_types": ["LASER", "MISSILE", "BEAM"]},
])

ZOLTAN_SHIP = ShipModel("Zoltan-Fregatte", 14, [
    Room("Schild", (50, 235, 85, 85)),
    Room("Super-Schild", (145, 235, 85, 85)),
    Room("Waffen", (240, 235, 85, 85)),
    Room("Brücke", (335, 235, 85, 85), max_power=2),
    Room("Medbay", (240, 140, 85, 85), max_power=2),
], max_weapons=4, max_crew=4, weapon_slots=[
    {"slot_id": 1, "pos": (282, 220), "allowed_types": ["BEAM", "LASER"]},
    {"slot_id": 2, "pos": (282, 335), "allowed_types": ["LASER", "BEAM", "MISSILE", "ION"]},
    {"slot_id": 3, "pos": (187, 220), "allowed_types": ["LASER"]},
    {"slot_id": 4, "pos": (377, 290), "allowed_types": ["MISSILE", "BEAM"]},
])

FEDERATION_SHIP = ShipModel("Federations-Kreuzer", 20, [
    Room("Artillerie", (50, 235, 85, 85)),
    Room("Schild", (145, 235, 85, 85)),
    Room("Waffen", (240, 235, 85, 85)),
    Room("Brücke", (335, 235, 85, 85), max_power=2),
    Room("Medbay", (50, 140, 85, 85), max_power=3),
], max_weapons=4, max_crew=5, weapon_slots=[
    {"slot_id": 1, "pos": (282, 220), "allowed_types": ["LASER", "BEAM", "MISSILE"]},
    {"slot_id": 2, "pos": (282, 335), "allowed_types": ["LASER", "BEAM", "MISSILE"]},
    {"slot_id": 3, "pos": (92, 220), "allowed_types": ["BEAM"]},
    {"slot_id": 4, "pos": (377, 290), "allowed_types": ["LASER", "MISSILE"]},
])

MANTIS_SHIP = ShipModel("Mantis-Kaperer", 16, [
    Room("Teleporter", (50, 235, 85, 85), max_power=2),
    Room("Schild", (145, 235, 85, 85)),
    Room("Waffen", (240, 235, 85, 85)),
    Room("Brücke", (335, 235, 85, 85), max_power=2),
    Room("Medbay", (145, 140, 85, 85), max_power=2),
    Room("Sensoren", (240, 140, 85, 85), max_power=2),
], max_weapons=3, max_crew=5, weapon_slots=[
    {"slot_id": 1, "pos": (282, 220), "allowed_types": ["LASER", "MISSILE", "FLAK"]},
    {"slot_id": 2, "pos": (282, 335), "allowed_types": ["LASER", "BEAM"]},
    {"slot_id": 3, "pos": (187, 220), "allowed_types": ["MISSILE", "BEAM"]},
])

ROCK_SHIP = ShipModel("Rock-Schlachtschiff", 22, [
    Room("Schild", (50, 235, 85, 85)),
    Room("Waffen", (145, 235, 85, 85)),
    Room("Maschinen", (240, 235, 85, 85)),
    Room("Brücke", (335, 235, 85, 85), max_power=2),
    Room("Medbay", (145, 140, 85, 85), max_power=2),
    Room("Teleporter", (240, 140, 85, 85), max_power=1),
], max_weapons=4, max_crew=6, weapon_slots=[
    {"slot_id": 1, "pos": (187, 220), "allowed_types": ["MISSILE", "FLAK", "LASER"]},
    {"slot_id": 2, "pos": (187, 335), "allowed_types": ["MISSILE", "LASER", "BOMB"]},
    {"slot_id": 3, "pos": (282, 220), "allowed_types": ["FLAK", "BEAM"]},
    {"slot_id": 4, "pos": (377, 290), "allowed_types": ["LASER", "MISSILE"]},
])

CRYSTAL_SHIP = ShipModel("Kristall-Kreuzer", 17, [
    Room("Schild", (50, 235, 85, 85)),
    Room("Super-Schild", (145, 235, 85, 85)),
    Room("Waffen", (240, 235, 85, 85)),
    Room("Brücke", (335, 235, 85, 85), max_power=2),
    Room("Medbay", (145, 140, 85, 85), max_power=2),
    Room("Tarnung", (240, 140, 85, 85), max_power=2),
    Room("Teleporter", (335, 140, 85, 85), max_power=1),
], max_weapons=4, max_crew=4, weapon_slots=[
    {"slot_id": 1, "pos": (282, 220), "allowed_types": ["LASER", "BEAM", "MISSILE"]},
    {"slot_id": 2, "pos": (282, 335), "allowed_types": ["LASER", "BEAM"]},
    {"slot_id": 3, "pos": (187, 220), "allowed_types": ["BEAM", "ION"]},
    {"slot_id": 4, "pos": (377, 290), "allowed_types": ["LASER", "MISSILE"]},
])

SHIP_BLUEPRINTS = {
    "Kestrel": PLAYER_SHIP,
    "Kreuzer": CRUISER_SHIP,
    "Tarnschiff": STEALTH_SHIP,
    "Zoltan-Fregatte": ZOLTAN_SHIP,
    "Federations-Kreuzer": FEDERATION_SHIP,
    "Mantis-Kaperer": MANTIS_SHIP,
    "Rock-Schlachtschiff": ROCK_SHIP,
    "Kristall-Kreuzer": CRYSTAL_SHIP,
}

SHIP_STARTING_SPECS: dict[str, dict[str, str | list[str]]] = {
    "Kestrel": {
        "crew_summary": "1x Mensch, 1x Engi",
        "crew_species": ["Mensch", "Engi"],
        "weapons_summary": "Standard Laser (3.0s), Artemis Rakete (4.0s)",
        "desc": "Ausgewogener Allrounder der Föderation mit solider Hülle und Raketen-Unterstützung.",
    },
    "Kreuzer": {
        "crew_summary": "2x Mensch, 1x Rock",
        "crew_species": ["Mensch", "Mensch", "Rock"],
        "weapons_summary": "Schwerer Laser (3.5s), Burst Laser MK II (4.0s)",
        "desc": "Schwer gepanzertes Kampfschiff mit erstklassigen Waffenbänken.",
    },
    "Tarnschiff": {
        "crew_summary": "1x Mensch, 1x Zoltan, 1x Engi",
        "crew_species": ["Mensch", "Zoltan", "Engi"],
        "weapons_summary": "Impuls-Laser (Kurz, 2.5s), Pike Strahl (5.0s)",
        "desc": "Spezialisiert auf Tarntechnologie und präzise Laserstrahl-Angriffe.",
    },
    "Zoltan-Fregatte": {
        "crew_summary": "3x Zoltan, 1x Mensch",
        "crew_species": ["Zoltan", "Zoltan", "Zoltan", "Mensch"],
        "weapons_summary": "Halberd Strahl (5.5s), Ion Blast MK I (3.0s)",
        "desc": "Ausgestattet mit Zoltan-Energieschilden und hohem Energie-Output.",
    },
    "Federations-Kreuzer": {
        "crew_summary": "1x Mensch, 1x Engi, 1x Mantis, 1x Rock",
        "crew_species": ["Mensch", "Engi", "Mantis", "Rock"],
        "weapons_summary": "Standard Laser (3.0s), Burst Laser MK II (4.0s)",
        "desc": "Multikulturelle Flotte mit Artillerie-Vortrieb und mächtigen Zusatzsystemen.",
    },
    "Mantis-Kaperer": {
        "crew_summary": "3x Mantis, 1x Engi, 1x Mensch",
        "crew_species": ["Mantis", "Mantis", "Mantis", "Engi", "Mensch"],
        "weapons_summary": "Kurzstrecken-Flak (3.2s), Brand-Laser MK I (3.8s)",
        "desc": "Agiles Enterschiff mit Teleporter und hoher Nahkampfstärke.",
    },
    "Rock-Schlachtschiff": {
        "crew_summary": "3x Rock, 1x Mensch",
        "crew_species": ["Rock", "Rock", "Rock", "Mensch"],
        "weapons_summary": "Hermes Rakete (4.5s), Hüllenbruch-Bombe (5.0s)",
        "desc": "Massive Panzerung und zerstörerische Raketenkanonen.",
    },
    "Kristall-Kreuzer": {
        "crew_summary": "2x Kristall, 1x Mensch, 1x Zoltan",
        "crew_species": ["Kristall", "Kristall", "Mensch", "Zoltan"],
        "weapons_summary": "Schwerer Laser (3.5s), Impuls-Laser (Kurz, 2.5s)",
        "desc": "Legendäres Alien-Schiff mit Kristallschilden und Spezialbewaffnung.",
    },
}


def apply_starting_setup_for_ship(player_data: Any, ship_name: str) -> None:
    from classes.Crew import Crew
    from classes.Weapon import Weapon

    player = getattr(player_data, "player", player_data)

    specs = SHIP_STARTING_SPECS.get(ship_name, SHIP_STARTING_SPECS["Kestrel"])
    species_list = specs["crew_species"]

    # Start-Crew setzen
    player.crew.clear()
    rooms = getattr(player.ship, "rooms", [])
    for idx, spec in enumerate(species_list):
        r = rooms[idx % len(rooms)] if rooms else None
        cx = r.rect.centerx if r else 250
        cy = r.rect.centery if r else 250
        player.crew.append(Crew(cx, cy, species=spec))

    # Start-Waffen setzen
    assert player.weapons is not None
    player.weapons.clear()
    if ship_name == "Kestrel":
        player.weapons = [
            Weapon("Standard Laser", charge_time=3.0, w_type="LASER", damage=25.0, max_range=650.0),
            Weapon("Artemis Rakete", charge_time=4.0, w_type="MISSILE", ammo_cost=1, damage=35.0, max_range=600.0),
        ]
    elif ship_name == "Kreuzer":
        player.weapons = [
            Weapon("Schwerer Laser", charge_time=3.5, w_type="LASER", damage=45.0, max_range=600.0),
            Weapon("Burst Laser MK II", charge_time=4.0, w_type="LASER", damage=60.0, max_range=600.0),
        ]
    elif ship_name == "Tarnschiff":
        player.weapons = [
            Weapon("Impuls-Laser (Kurz)", charge_time=2.5, w_type="LASER", damage=25.0, max_range=600.0),
            Weapon("Pike Strahl", charge_time=5.0, w_type="BEAM", damage=35.0, max_range=600.0),
        ]
    elif ship_name == "Zoltan-Fregatte":
        player.weapons = [
            Weapon("Halberd Strahl", charge_time=5.5, w_type="BEAM", damage=45.0, max_range=600.0),
            Weapon("Ion Blast MK I", charge_time=3.0, w_type="ION", damage=10.0, max_range=600.0),
        ]
    elif ship_name == "Federations-Kreuzer":
        player.weapons = [
            Weapon("Standard Laser", charge_time=3.0, w_type="LASER", damage=25.0, max_range=650.0),
            Weapon("Burst Laser MK II", charge_time=4.0, w_type="LASER", damage=60.0, max_range=600.0),
        ]
    elif ship_name == "Mantis-Kaperer":
        player.weapons = [
            Weapon("Kurzstrecken-Flak", charge_time=3.2, w_type="FLAK", damage=30.0, max_range=550.0),
            Weapon("Brand-Laser MK I", charge_time=3.8, w_type="LASER", damage=15.0, fire_chance=0.75, max_range=600.0),
        ]
    elif ship_name == "Rock-Schlachtschiff":
        player.weapons = [
            Weapon("Hermes Rakete", charge_time=4.5, w_type="MISSILE", ammo_cost=1, damage=50.0, max_range=600.0),
            Weapon("Hüllenbruch-Bombe", charge_time=5.0, w_type="BOMB", ammo_cost=1, damage=15.0, breach_chance=0.90, max_range=550.0),
        ]
    elif ship_name == "Kristall-Kreuzer":
        player.weapons = [
            Weapon("Schwerer Laser", charge_time=3.5, w_type="LASER", damage=45.0, max_range=600.0),
            Weapon("Impuls-Laser (Kurz)", charge_time=2.5, w_type="LASER", damage=25.0, max_range=600.0),
        ]


ENEMY_SCOUT = ShipModel("Scout", 8, [
    Room("Schild", (600, 220, 80, 80), is_enemy=True),
    Room("Waffen", (690, 220, 80, 80), is_enemy=True),
    Room("Brücke", (780, 220, 80, 80), is_enemy=True)
], is_enemy=True)

ENEMY_FIGHTER = ShipModel("Rebellen Jäger", 12, [
    Room("Schild", (580, 210, 85, 85), is_enemy=True),
    Room("Waffen", (675, 210, 85, 85), is_enemy=True),
    Room("Antrieb", (770, 210, 85, 85), is_enemy=True)
], is_enemy=True)

ENEMY_BOMBER = ShipModel("Kaper-Bomber", 14, [
    Room("Schild", (570, 200, 90, 90), is_enemy=True),
    Room("Raketen", (670, 200, 90, 90), is_enemy=True),
    Room("Brücke", (770, 200, 90, 90), is_enemy=True)
], is_enemy=True)

ENEMY_CRUISER = ShipModel("Schwerer Kreuzer", 18, [
    Room("Schild", (550, 160, 95, 95), is_enemy=True),
    Room("Waffen", (655, 160, 95, 95), is_enemy=True),
    Room("Maschinen", (760, 160, 95, 95), is_enemy=True)
], is_enemy=True)

ENEMY_MANTIS_BOARDER = ShipModel("Mantis-Kaperer", 16, [
    Room("Schild", (550, 170, 85, 85), is_enemy=True),
    Room("Teleporter", (645, 170, 85, 85), is_enemy=True),
    Room("Waffen", (740, 170, 85, 85), is_enemy=True)
], is_enemy=True)

ENEMY_ZOLTAN_FRIGATE = ShipModel("Zoltan-Fregatte", 14, [
    Room("Schild", (560, 180, 80, 80), max_power=3, is_enemy=True),
    Room("Waffen", (650, 180, 80, 80), is_enemy=True),
    Room("Brücke", (740, 180, 80, 80), is_enemy=True)
], is_enemy=True)

ENEMY_ROCK_WARSHIP = ShipModel("Rock-Kriegsschiff", 22, [
    Room("Schild", (540, 150, 95, 95), is_enemy=True),
    Room("Waffen", (645, 150, 95, 95), is_enemy=True),
    Room("Maschinen", (750, 150, 95, 95), is_enemy=True)
], is_enemy=True)

ENEMY_DRONE_CARRIER = ShipModel("Drohnen-Träger", 16, [
    Room("Schild", (550, 170, 85, 85), is_enemy=True),
    Room("Drohnen-Kontrolle", (645, 170, 85, 85), is_enemy=True),
    Room("Brücke", (740, 170, 85, 85), is_enemy=True)
], is_enemy=True)

MINI_BOSS_SECTOR_1 = ShipModel("Elite-Kaperer (Mini-Boss)", 16, [
    Room("Schild", (560, 170, 90, 90), is_enemy=True),
    Room("Waffen", (660, 170, 90, 90), is_enemy=True),
    Room("Brücke", (760, 170, 90, 90), is_enemy=True)
], is_enemy=True)

MINI_BOSS_SECTOR_2 = ShipModel("Zerstörer (Mini-Boss)", 22, [
    Room("Schild", (550, 150, 95, 95), is_enemy=True),
    Room("Waffen", (655, 150, 95, 95), is_enemy=True),
    Room("Brücke", (760, 150, 95, 95), is_enemy=True)
], is_enemy=True)

ENEMY_BOSS = ShipModel("Flaggschiff", 25, [
    Room("Schild", (550, 150, 100, 100), is_enemy=True),
    Room("Laser", (670, 100, 80, 80), is_enemy=True),
    Room("Raketen", (670, 200, 80, 80), is_enemy=True),
    Room("Brücke", (770, 150, 100, 100), is_enemy=True)
], is_enemy=True)

ENEMY_TEMPLATES = [
    ENEMY_SCOUT,
    ENEMY_FIGHTER,
    ENEMY_BOMBER,
    ENEMY_CRUISER,
    ENEMY_MANTIS_BOARDER,
    ENEMY_ZOLTAN_FRIGATE,
    ENEMY_ROCK_WARSHIP,
    ENEMY_DRONE_CARRIER,
]

