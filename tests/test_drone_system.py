import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.Drone import Drone, DRONE_CATALOG
from classes.GameData import GameData
from managers.combat_manager import CombatManager
from managers.state_manager import StateManager


class TestDroneSystem(unittest.TestCase):

    def setUp(self):
        self.data = GameData()
        self.state_mgr = StateManager(self.data)
        self.combat_mgr = CombatManager(self.data)

        # Give player ship Drone Control room power = 4
        drone_room = next((r for r in self.data.player.ship.rooms if r.name == "Drohnen-Kontrolle"), None)
        if drone_room:
            drone_room.current_power = 4

        self.data.player.drone_parts = 10  # 10 drone parts

    def test_drones_property_alias(self):
        self.assertEqual(self.data.player.drone_parts, 10)
        self.assertEqual(self.data.player.drones, 10)
        self.data.player.drones = 5
        self.assertEqual(self.data.player.drone_parts, 5)

    def test_drone_catalog_master(self):
        self.assertEqual(len(DRONE_CATALOG), 5, "Catalog should have 5 drone types.")
        types = [d.drone_type for d in DRONE_CATALOG]
        self.assertIn("COMBAT_MK1", types)
        self.assertIn("REPAIR", types)
        self.assertIn("DEFENSE_MK1", types)
        self.assertIn("SHIELD_CHARGER", types)
        self.assertIn("ANTI_PERSONNEL", types)

    def test_toggle_drones_resource_consumption(self):
        # Toggle combat drone (1 Power, 1 Drone part)
        initial_drones = self.data.player.drone_parts
        self.combat_mgr.toggle_combat_drone()
        self.assertTrue(self.data.combat.combat_drone_active)
        self.assertEqual(self.data.player.drone_parts, initial_drones - 1)

        # Toggle defense drone (2 Power, 1 Drone part)
        self.combat_mgr.toggle_defense_drone()
        self.assertTrue(self.data.combat.defense_drone_active)
        self.assertEqual(self.data.player.drone_parts, initial_drones - 2)

    def test_drone_power_limit_enforcement(self):
        # Set Drone Control power to 1
        drone_room = next((r for r in self.data.player.ship.rooms if r.name == "Drohnen-Kontrolle"), None)
        if drone_room:
            drone_room.current_power = 1

        self.combat_mgr.toggle_combat_drone()  # Uses 1 power -> OK
        self.assertTrue(self.data.combat.combat_drone_active)

        # Trying to toggle defense drone (needs 2 power) should fail
        self.combat_mgr.toggle_defense_drone()
        self.assertFalse(self.data.combat.defense_drone_active, "Defense drone should fail to activate when power limit is exceeded.")

    def test_defense_drone_shoots_incoming_missile(self):
        self.combat_mgr.toggle_defense_drone()
        self.assertTrue(self.data.combat.defense_drone_active)

        # Spawn incoming enemy missile near player ship
        from classes.Projectile import Projectile
        missile = Projectile((300, 245), (220, 245), target_room=self.data.player.ship.rooms[0], is_player_shot=False, w_type="MISSILE")
        self.data.player.projectiles.append(missile)

        # Update drone AI
        self.combat_mgr.update_drones(0.1)

        # Missile should be shot down (alive = False)
        self.assertFalse(missile.alive, "Defense drone should shoot down incoming missile.")


if __name__ == "__main__":
    unittest.main()
