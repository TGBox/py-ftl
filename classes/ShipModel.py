import copy

from classes.Door import Door
from classes.Room import Room


class ShipModel:
    def __init__(
        self,
        name: str,
        max_hp: int,
        rooms: list[Room],
        is_enemy: bool = False,
        max_weapons: int = 3,
        max_crew: int = 4,
        weapon_slots: list[dict] | None = None,
    ):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.rooms = rooms
        self.is_enemy = is_enemy
        self.max_weapons = max_weapons
        self.max_crew = max_crew
        self.weapon_slots: list[dict] = weapon_slots or []
        self.doors: list[Door] = []
        self.generate_doors()
        if not self.weapon_slots:
            self.generate_default_weapon_slots()

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

    def update_doors(self, dt: float) -> None:
        for d in self.doors:
            d.update(dt)

    def draw_doors(self, surface) -> None:
        for d in self.doors:
            d.draw(surface)

    def open_all_doors(self) -> None:
        for d in self.doors:
            if not d.is_airlock:
                d.is_open = True

    def close_all_doors(self) -> None:
        for d in self.doors:
            d.is_open = False

    def open_airlocks(self) -> None:
        for d in self.doors:
            if d.is_airlock:
                d.is_open = not d.is_open


PLAYER_SHIP = ShipModel("Kestrel", 15, [
    Room("Schild", (60, 200, 90, 90)),
    Room("Waffen", (160, 200, 90, 90)),
    Room("Brücke", (260, 200, 90, 90), max_power=2),
    Room("Medbay", (160, 100, 90, 90), max_power=2),
    Room("Teleporter", (260, 100, 90, 90), max_power=1),
    Room("Tarnung", (60, 100, 90, 90), max_power=2),
    Room("Sensoren", (360, 200, 90, 90), max_power=2),
], max_weapons=3, max_crew=4, weapon_slots=[
    {"slot_id": 1, "pos": (205, 185), "allowed_types": ["LASER", "BEAM", "MISSILE"]},
    {"slot_id": 2, "pos": (205, 305), "allowed_types": ["LASER", "MISSILE"]},
    {"slot_id": 3, "pos": (335, 245), "allowed_types": ["MISSILE", "BEAM"]},
])

CRUISER_SHIP = ShipModel("Kreuzer", 18, [
    Room("Schild", (50, 190, 85, 85)),
    Room("Waffen", (145, 190, 85, 85)),
    Room("Maschinen", (240, 190, 85, 85)),
    Room("Brücke", (335, 190, 85, 85), max_power=2),
    Room("Medbay", (145, 95, 85, 85), max_power=2),
], max_weapons=4, max_crew=6, weapon_slots=[
    {"slot_id": 1, "pos": (187, 175), "allowed_types": ["LASER", "BEAM", "MISSILE"]},
    {"slot_id": 2, "pos": (187, 290), "allowed_types": ["LASER", "BEAM"]},
    {"slot_id": 3, "pos": (282, 175), "allowed_types": ["MISSILE", "BEAM"]},
    {"slot_id": 4, "pos": (377, 245), "allowed_types": ["LASER", "MISSILE"]},
])

STEALTH_SHIP = ShipModel("Tarnschiff", 12, [
    Room("Tarnung", (70, 200, 80, 80)),
    Room("Waffen", (160, 200, 80, 80)),
    Room("Brücke", (250, 200, 80, 80), max_power=2),
    Room("Medbay", (160, 110, 80, 80), max_power=1),
], max_weapons=3, max_crew=3, weapon_slots=[
    {"slot_id": 1, "pos": (200, 185), "allowed_types": ["LASER", "BEAM"]},
    {"slot_id": 2, "pos": (200, 295), "allowed_types": ["BEAM"]},
    {"slot_id": 3, "pos": (290, 240), "allowed_types": ["LASER", "MISSILE"]},
])

ZOLTAN_SHIP = ShipModel("Zoltan-Fregatte", 14, [
    Room("Schild", (50, 190, 85, 85)),
    Room("Super-Schild", (145, 190, 85, 85)),
    Room("Waffen", (240, 190, 85, 85)),
    Room("Brücke", (335, 190, 85, 85), max_power=2),
    Room("Medbay", (240, 95, 85, 85), max_power=2),
], max_weapons=4, max_crew=4, weapon_slots=[
    {"slot_id": 1, "pos": (282, 175), "allowed_types": ["BEAM", "LASER"]},
    {"slot_id": 2, "pos": (282, 290), "allowed_types": ["LASER", "BEAM", "MISSILE"]},
    {"slot_id": 3, "pos": (187, 175), "allowed_types": ["LASER"]},
    {"slot_id": 4, "pos": (377, 245), "allowed_types": ["MISSILE", "BEAM"]},
])

FEDERATION_SHIP = ShipModel("Federations-Kreuzer", 20, [
    Room("Artillerie", (50, 190, 85, 85)),
    Room("Schild", (145, 190, 85, 85)),
    Room("Waffen", (240, 190, 85, 85)),
    Room("Brücke", (335, 190, 85, 85), max_power=2),
    Room("Medbay", (50, 95, 85, 85), max_power=3),
], max_weapons=4, max_crew=5, weapon_slots=[
    {"slot_id": 1, "pos": (282, 175), "allowed_types": ["LASER", "BEAM", "MISSILE"]},
    {"slot_id": 2, "pos": (282, 290), "allowed_types": ["BEAM", "MISSILE"]},
    {"slot_id": 3, "pos": (92, 175), "allowed_types": ["BEAM"]},
    {"slot_id": 4, "pos": (377, 245), "allowed_types": ["LASER", "MISSILE"]},
])

SHIP_BLUEPRINTS = {
    "Kestrel": PLAYER_SHIP,
    "Kreuzer": CRUISER_SHIP,
    "Tarnschiff": STEALTH_SHIP,
    "Zoltan-Fregatte": ZOLTAN_SHIP,
    "Federations-Kreuzer": FEDERATION_SHIP,
}


ENEMY_SCOUT = ShipModel("Scout", 8, [
    Room("Schild", (600, 200, 80, 80), is_enemy=True),
    Room("Waffen", (690, 200, 80, 80), is_enemy=True),
    Room("Brücke", (780, 200, 80, 80), is_enemy=True)
], is_enemy=True)

ENEMY_FIGHTER = ShipModel("Rebellen Jäger", 12, [
    Room("Schild", (580, 190, 85, 85), is_enemy=True),
    Room("Waffen", (675, 190, 85, 85), is_enemy=True),
    Room("Antrieb", (770, 190, 85, 85), is_enemy=True)
], is_enemy=True)

ENEMY_BOMBER = ShipModel("Kaper-Bomber", 14, [
    Room("Schild", (570, 180, 90, 90), is_enemy=True),
    Room("Raketen", (670, 180, 90, 90), is_enemy=True),
    Room("Brücke", (770, 180, 90, 90), is_enemy=True)
], is_enemy=True)

ENEMY_CRUISER = ShipModel("Schwerer Kreuzer", 18, [
    Room("Schild", (550, 160, 95, 95), is_enemy=True),
    Room("Waffen", (655, 160, 95, 95), is_enemy=True),
    Room("Maschinen", (760, 160, 95, 95), is_enemy=True)
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

ENEMY_TEMPLATES = [ENEMY_SCOUT, ENEMY_FIGHTER, ENEMY_BOMBER, ENEMY_CRUISER]
