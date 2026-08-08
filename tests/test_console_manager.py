import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.GameData import GameData
from managers.console_manager import ConsoleManager


class TestConsoleManager(unittest.TestCase):

    def setUp(self):
        self.data = GameData()
        self.console = ConsoleManager(self.data)

    def test_console_toggle(self):
        self.assertFalse(self.console.active)
        self.console.toggle()
        self.assertTrue(self.console.active)

    def test_cheat_resource_commands(self):
        init_scrap = self.data.player.scrap
        self.console.execute_command("scrap 200")
        self.assertEqual(self.data.player.scrap, init_scrap + 200)

        # Test alias 'geld'
        self.console.execute_command("geld 300")
        self.assertEqual(self.data.player.scrap, init_scrap + 500)

        init_fuel = self.data.player.fuel
        self.console.execute_command("fuel 15")
        self.assertEqual(self.data.player.fuel, init_fuel + 15)

        init_missiles = self.data.player.missiles
        self.console.execute_command("missiles 10")
        self.assertEqual(self.data.player.missiles, init_missiles + 10)

        init_drones = self.data.player.drone_parts
        self.console.execute_command("drones 5")
        self.assertEqual(self.data.player.drone_parts, init_drones + 5)

    def test_cheat_weapon_upgrade_level5(self):
        from classes.Weapon import Weapon
        w = Weapon("Laser I", charge_time=4.0, w_type="LASER", level=1)
        self.data.player.weapons = [w]

        self.console.execute_command("waffen5")
        self.assertEqual(self.data.player.weapons[0].level, 5)
        self.assertIn("MK V", self.data.player.weapons[0].name)

    def test_cheat_godmode_and_heal(self):
        self.console.execute_command("godmode")
        self.assertTrue(getattr(self.data.player, "godmode", False))

        self.data.player.ship.hp = 1
        self.console.execute_command("heal")
        self.assertEqual(self.data.player.ship.hp, self.data.player.ship.max_hp)

    def test_cheat_unlock_all(self):
        self.console.execute_command("unlock_all")
        self.assertEqual(len(self.data.player.unlocked_ships), 8)

    def test_fun_cheats(self):
        self.console.execute_command("party")
        self.assertTrue(getattr(self.data, "party_mode", False))

        self.console.execute_command("turbo")
        self.assertTrue(getattr(self.data, "turbo_mode", False))


if __name__ == "__main__":
    unittest.main()
