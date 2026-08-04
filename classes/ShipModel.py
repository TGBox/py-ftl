import copy

from classes.Room import Room


class ShipModel:
    def __init__(self, name: str, max_hp: int, rooms: list[Room], is_enemy: bool = False):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.rooms = rooms
        self.is_enemy = is_enemy
        
# Beispiel für alternative Schiffsklassen / Layouts
#CUSTOM_SHIP_LAYOUTS = {
#    "Kestrel": {
#        "max_hp": 30,
#        "rooms_config": [
#            {"type": "SHIELD", "pos": (180, 200), "size": (50, 50)},
#            {"type": "WEAPON", "pos": (240, 200), "size": (50, 50)},
#            {"type": "PILOT", "pos": (120, 200), "size": (50, 50)},
#        ],
#    },
#    "Cruiser": {
#        "max_hp": 35,
#        "rooms_config": [
#            {"type": "SHIELD", "pos": (170, 190), "size": (60, 50)},
#            {"type": "WEAPON", "pos": (240, 190), "size": (50, 50)},
#            {"type": "PILOT", "pos": (110, 190), "size": (50, 50)},
#        ],
#    },
#}

PLAYER_SHIP = ShipModel("Kestrel", 15, [
    Room("Schild", (60, 200, 90, 90)),
    Room("Waffen", (160, 200, 90, 90)),
    Room("Brücke", (260, 200, 90, 90), max_power=2)
])

ENEMY_SCOUT = ShipModel("Scout", 8, [
    Room("Schild", (600, 200, 80, 80), is_enemy=True),
    Room("Waffen", (690, 200, 80, 80), is_enemy=True),
    Room("Brücke", (780, 200, 80, 80), is_enemy=True)
], is_enemy=True)

ENEMY_BOSS = ShipModel("Flaggschiff", 25, [
    Room("Schild", (550, 150, 100, 100), is_enemy=True),
    Room("Laser", (670, 100, 80, 80), is_enemy=True),
    Room("Raketen", (670, 200, 80, 80), is_enemy=True),
    Room("Brücke", (770, 150, 100, 100), is_enemy=True)
], is_enemy=True)

# Standardgegner für den Start festlegen
current_enemy: ShipModel = copy.deepcopy(ENEMY_SCOUT)