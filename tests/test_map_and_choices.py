import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.GameData import GameData
from managers.map_manager import MapManager
from settings import STATE_COMBAT, STATE_EVENT, STATE_MAP, STATE_SHOP


class TestMapAndChoices(unittest.TestCase):

    def setUp(self):
        self.data = GameData()
        self.map_manager = MapManager(self.data)

    def test_travel_to_node_fuel_consumption(self):
        self.data.player.fuel = 5
        start_node = self.data.world.star_map.current_node
        self.assertIsNotNone(start_node)
        assert start_node is not None
        self.assertGreater(len(start_node.connections), 0)

        target_node = start_node.connections[0]
        success = self.map_manager.travel_to_node(target_node)

        self.assertTrue(success)
        self.assertEqual(self.data.player.fuel, 4)
        self.assertEqual(self.data.world.star_map.current_node, target_node)

    def test_travel_to_node_no_fuel_trigger(self):
        self.data.player.fuel = 0
        start_node = self.data.world.star_map.current_node
        assert start_node is not None
        target_node = start_node.connections[0]

        success = self.map_manager.travel_to_node(target_node)
        self.assertFalse(success)
        self.assertEqual(self.data.current_state, STATE_EVENT)
        self.assertIn("KEIN TREIBSTOFF MEHR", self.data.world.event_manager.current_event_text)

    def test_handle_choice_claim_resources(self):
        self.data.player.scrap = 50
        self.data.player.fuel = 5
        self.data.player.missiles = 2

        choice_data = {"scrap": 25, "fuel": 2, "missiles": 1}
        self.map_manager.handle_choice("CLAIM_RESOURCES", choice_data)

        self.assertEqual(self.data.player.scrap, 75)
        self.assertEqual(self.data.player.fuel, 7)
        self.assertEqual(self.data.player.missiles, 3)

    def test_handle_choice_buy_fuel(self):
        self.data.player.scrap = 30
        self.data.player.fuel = 2

        choice_data = {}
        self.map_manager.handle_choice("BUY_FUEL", choice_data)

        self.assertEqual(self.data.player.scrap, 20)
        self.assertEqual(self.data.player.fuel, 4)

    def test_can_afford_choice(self):
        from utils import can_afford_choice
        self.data.player.scrap = 5
        self.data.player.fuel = 1

        costly_choice = {"action": "GIVE_RESOURCES", "scrap": -10}
        affordable_choice = {"action": "GIVE_RESOURCES", "scrap": -5}

        self.assertFalse(can_afford_choice(costly_choice, self.data.player))
        self.assertTrue(can_afford_choice(affordable_choice, self.data.player))

    def test_non_negative_resource_clamping(self):
        self.data.player.scrap = 5
        choice_data = {"scrap": -20}
        self.map_manager.handle_choice("GIVE_RESOURCES", choice_data)
        self.assertEqual(self.data.player.scrap, 0, "Scrap must never become negative.")

    def test_handle_choice_take_damage(self):
        self.data.player.ship.hp = 15
        self.data.player.scrap = 20

        choice_data = {"damage": 5, "cost_scrap": 10}
        self.map_manager.handle_choice("TAKE_DAMAGE", choice_data)

        self.assertEqual(self.data.player.ship.hp, 10)
        self.assertEqual(self.data.player.scrap, 10)

    def test_handle_choice_start_combat(self):
        choice_data = {}
        self.map_manager.handle_choice("START_COMBAT", choice_data)

        self.assertEqual(self.data.current_state, STATE_COMBAT)

    def test_handle_choice_flee_outcomes(self):
        choice_data = {"is_escape": True}
        # Run 20 flee choices to ensure both successful escapes and failures occur without error
        for _ in range(20):
            self.map_manager.handle_choice("FLEE", choice_data)
            self.assertIsNotNone(self.data.world.event_manager.result_text)


if __name__ == "__main__":
    unittest.main()
