import copy

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
    ):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.rooms = rooms
        self.is_enemy = is_enemy
        self.max_weapons = max_weapons
        self.max_crew = max_crew


PLAYER_SHIP = ShipModel("Kestrel", 15, [
    Room("Schild", (60, 200, 90, 90)),
    Room("Waffen", (160, 200, 90, 90)),
    Room("Brücke", (260, 200, 90, 90), max_power=2)
], max_weapons=3, max_crew=4)

CRUISER_SHIP = ShipModel("Kreuzer", 18, [
    Room("Schild", (50, 190, 85, 85)),
    Room("Waffen", (145, 190, 85, 85)),
    Room("Maschinen", (240, 190, 85, 85)),
    Room("Brücke", (335, 190, 85, 85), max_power=2)
], max_weapons=4, max_crew=6)

STEALTH_SHIP = ShipModel("Tarnschiff", 12, [
    Room("Tarnung", (70, 200, 80, 80)),
    Room("Waffen", (160, 200, 80, 80)),
    Room("Brücke", (250, 200, 80, 80), max_power=2)
], max_weapons=3, max_crew=3)

SHIP_BLUEPRINTS = {
    "Kestrel": PLAYER_SHIP,
    "Kreuzer": CRUISER_SHIP,
    "Tarnschiff": STEALTH_SHIP,
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

ENEMY_BOSS = ShipModel("Flaggschiff", 25, [
    Room("Schild", (550, 150, 100, 100), is_enemy=True),
    Room("Laser", (670, 100, 80, 80), is_enemy=True),
    Room("Raketen", (670, 200, 80, 80), is_enemy=True),
    Room("Brücke", (770, 150, 100, 100), is_enemy=True)
], is_enemy=True)

ENEMY_TEMPLATES = [ENEMY_SCOUT, ENEMY_FIGHTER, ENEMY_BOMBER, ENEMY_CRUISER]