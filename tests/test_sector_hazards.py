import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.GameData import GameData
from classes.StarMap import StarMap
from managers.combat_manager import CombatManager
from managers.state_manager import StateManager


class TestSectorHazards(unittest.TestCase):

    def setUp(self):
        self.data = GameData()
        self.state_mgr = StateManager(self.data)
        self.combat_mgr = CombatManager(self.data, self.state_mgr)

    def test_sector_types_generation(self):
        starmap = StarMap()
        valid_sectors = ["Zivil-Sektor", "Rebellen-Sektor", "Nebel-Sektor", "Mantis-Jagdgebiet", "Kristall-Sektor"]
        self.assertIn(starmap.sector_type, valid_sectors)

        # Test sector progression updates sector types
        starmap.sector = 2
        starmap.generate_map()
        self.assertEqual(starmap.sector_type, "Rebellen-Sektor")

    def test_hazard_distribution_on_map(self):
        starmap = StarMap()
        hazard_nodes = [n for n in starmap.nodes if getattr(n, "hazard_type", "NONE") != "NONE"]
        self.assertGreater(len(hazard_nodes), 0, "Map generation should distribute hazards on nodes.")

        valid_hazards = ["SOLAR_FLARE", "ASTEROID_FIELD", "NEBULA_ION_STORM", "PULSAR"]
        for node in hazard_nodes:
            self.assertIn(node.hazard_type, valid_hazards)

    def test_nebula_ion_storm_halves_reactor_power(self):
        node = self.data.world.star_map.nodes[1]
        node.hazard_type = "NEBULA_ION_STORM"
        self.data.world.star_map.current_node = node
        self.data.current_state = "COMBAT"

        initial_power = self.data.player.reactor.total_power
        self.combat_mgr.update(0.1)

        expected_power = max(1, initial_power // 2)
        self.assertEqual(self.data.player.reactor.max_power, expected_power, "Ion storm should halve reactor max power.")

    def test_pulsar_radiation_ionizes_rooms(self):
        node = self.data.world.star_map.nodes[1]
        node.hazard_type = "PULSAR"
        self.data.world.star_map.current_node = node
        self.data.current_state = "COMBAT"
        self.data.combat.pulsar_timer = 0.05  # Force pulse trigger

        self.combat_mgr.update(0.1)

        ionized_rooms = [r for r in self.data.player.ship.rooms + self.data.enemy.ship.rooms if getattr(r, "ion_timer", 0.0) > 0.0]
        self.assertGreater(len(ionized_rooms), 0, "Pulsar radiation pulse should ionize system rooms.")


if __name__ == "__main__":
    unittest.main()
