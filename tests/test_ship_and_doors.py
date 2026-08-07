import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.Door import Door
from classes.Room import Room
from classes.ShipModel import PLAYER_SHIP, ShipModel


class TestShipAndDoors(unittest.TestCase):

    def setUp(self):
        self.ship = copy.deepcopy(PLAYER_SHIP)

    def test_door_generation(self):
        self.assertGreater(len(self.ship.doors), 0)
        interior_doors = [d for d in self.ship.doors if not d.is_airlock]
        airlocks = [d for d in self.ship.doors if d.is_airlock]

        self.assertGreater(len(interior_doors), 0, "Ship should have interior doors connecting adjacent rooms.")
        self.assertEqual(len(airlocks), 2, "Player ship should have 2 airlocks.")

    def test_door_toggling(self):
        # Open all doors
        self.ship.open_all_doors()
        for d in self.ship.doors:
            if not d.is_airlock:
                self.assertTrue(d.is_open)

        # Close all doors
        self.ship.close_all_doors()
        for d in self.ship.doors:
            self.assertFalse(d.is_open)

        # Open airlocks
        self.ship.open_airlocks()
        airlocks = [d for d in self.ship.doors if d.is_airlock]
        for a in airlocks:
            self.assertTrue(a.is_open)

    def test_swap_room_systems(self):
        r1 = self.ship.rooms[0]
        r2 = self.ship.rooms[1]
        name1, name2 = r1.name, r2.name

        self.ship.swap_room_systems(r1, r2)

        self.assertEqual(r1.name, name2)
        self.assertEqual(r2.name, name1)

    def test_all_ship_blueprints(self):
        from classes.ShipModel import SHIP_BLUEPRINTS

        self.assertEqual(len(SHIP_BLUEPRINTS), 8, "There should be exactly 8 ship blueprints.")
        expected_ships = [
            "Kestrel", "Kreuzer", "Tarnschiff", "Zoltan-Fregatte",
            "Federations-Kreuzer", "Mantis-Kaperer", "Rock-Schlachtschiff", "Kristall-Kreuzer"
        ]
        for ship_name in expected_ships:
            self.assertIn(ship_name, SHIP_BLUEPRINTS)
            blueprint = SHIP_BLUEPRINTS[ship_name]
            copied_ship = copy.deepcopy(blueprint)

            self.assertEqual(copied_ship.name, ship_name)
            self.assertGreater(copied_ship.hp, 0)
            self.assertGreater(len(copied_ship.rooms), 0)
            self.assertGreater(len(copied_ship.doors), 0)
            self.assertGreater(len(copied_ship.weapon_slots), 0)


if __name__ == "__main__":
    unittest.main()
