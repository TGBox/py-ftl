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
        assert self.data.player.weapons is not None and self.data.player.weapons[0] is not None
        self.assertEqual(self.data.player.weapons[0].level, 5)
        self.assertIn("MK V", self.data.player.weapons[0].name)

    def test_cheat_godmode_and_heal(self):
        self.console.execute_command("godmode")
        self.assertTrue(getattr(self.data.player, "godmode", False))

        self.data.player.ship.hp = 1
        self.console.execute_command("heal")
        self.assertEqual(self.data.player.ship.hp, self.data.player.ship.max_hp)

    def test_cheat_unlock_all(self):
        from unittest.mock import patch
        with patch("managers.save_manager.SaveManager.save_unlocks"):
            self.console.execute_command("unlock_all")
            self.assertEqual(len(self.data.player.unlocked_ships), 8)

    def test_fun_cheats(self):
        self.console.execute_command("party")
        self.assertTrue(getattr(self.data, "party_mode", False))

        self.console.execute_command("turbo")
        self.assertTrue(getattr(self.data, "turbo_mode", False))

    def test_console_scrolling_and_help_text(self):
        self.console.toggle()
        self.console.execute_command("help")
        # Help adds 11 lines, total history length >= 13
        self.assertGreaterEqual(len(self.console.history), 13)

        # Test PageUp scrolling
        event_pgup = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEUP)
        self.console.handle_keydown(event_pgup)
        self.assertGreater(self.console.scroll_offset, 0)

        # Test mouse wheel scrolling
        init_offset = self.console.scroll_offset
        self.console.handle_mouse_scroll(4) # Scroll Up
        self.assertGreaterEqual(self.console.scroll_offset, init_offset)

        # Executing a command resets scroll_offset to 0 (bottom)
        self.console.execute_command("heal")
        self.assertEqual(self.console.scroll_offset, 0)

    def test_command_history_recall(self):
        self.console.toggle()
        self.console.input_text = "scrap 100"
        event_ret = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        self.console.handle_keydown(event_ret)

        self.console.input_text = "heal"
        self.console.handle_keydown(event_ret)

        # Press UP arrow to recall "heal"
        event_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        self.console.handle_keydown(event_up)
        self.assertEqual(self.console.input_text, "heal")

        # Press UP arrow again to recall "scrap 100"
        self.console.handle_keydown(event_up)
        self.assertEqual(self.console.input_text, "scrap 100")

        # Press DOWN arrow to return to "heal"
        event_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        self.console.handle_keydown(event_down)
        self.assertEqual(self.console.input_text, "heal")


if __name__ == "__main__":
    unittest.main()
