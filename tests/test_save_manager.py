import os
import sys
import unittest

from game import Game

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.GameData import GameData
from managers.save_manager import SaveManager


class TestSaveManager(unittest.TestCase):

    def setUp(self):
        self.test_save_file = "test_savegame_tmp.dat"
        self.test_unlock_file = "test_unlocks_tmp.json"

    def tearDown(self):
        if os.path.exists(self.test_save_file):
            os.remove(self.test_save_file)
        if os.path.exists(self.test_unlock_file):
            os.remove(self.test_unlock_file)

    def test_save_and_load_unlocks(self):
        ships = ["Kestrel", "Kreuzer", "Tarnschiff"]
        self.assertTrue(SaveManager.save_unlocks(ships, self.test_unlock_file))

        loaded = SaveManager.load_unlocks(self.test_unlock_file)
        self.assertEqual(loaded, ships)

    def test_save_and_load_game_roundtrip(self):
        data = GameData()
        game = Game()
        data.player.scrap = 350
        data.player.fuel = 18
        data.world.star_map.sector = 3

        # Save game
        self.assertTrue(SaveManager.save_game(data, game, self.test_save_file))
        self.assertTrue(SaveManager.has_savegame(self.test_save_file))

        # Load into new GameData instance
        loaded_data = GameData()
        self.assertTrue(SaveManager.load_game(loaded_data, self.test_save_file))

        self.assertEqual(loaded_data.player.scrap, 350)
        self.assertEqual(loaded_data.player.fuel, 18)
        self.assertEqual(loaded_data.world.star_map.sector, 3)

    def test_auto_save_setting_roundtrip(self):
        data = GameData()
        game = Game()
        self.assertFalse(data.auto_save_enabled)

        data.auto_save_enabled = True
        self.assertTrue(SaveManager.save_game(data, game, self.test_save_file))

        loaded_data = GameData()
        self.assertTrue(SaveManager.load_game(loaded_data, self.test_save_file))
        self.assertTrue(loaded_data.auto_save_enabled)

    def test_tampered_save_rejection(self):
        data = GameData()
        game = Game()
        SaveManager.save_game(data, game, self.test_save_file)

        # Corrupt bytes in save file
        with open(self.test_save_file, "r+b") as f:
            f.seek(20)
            f.write(b"CORRUPTED_BYTES_HERE")

        loaded_data = GameData()
        self.assertFalse(SaveManager.load_game(loaded_data, self.test_save_file))


    def test_emergency_save_slot_4(self):
        data = GameData()
        game = Game()
        data.player.scrap = 999

        # Ensure slot 4 path is cleaned up afterwards
        slot_4_path = SaveManager.get_slot_filepath(4)
        if os.path.exists(slot_4_path):
            os.remove(slot_4_path)

        try:
            self.assertTrue(SaveManager.save_emergency_game(data, game))
            self.assertTrue(SaveManager.has_savegame(4))

            loaded_data = GameData()
            self.assertTrue(SaveManager.load_game(loaded_data, slot=4))
            self.assertEqual(loaded_data.player.scrap, 999)
        finally:
            if os.path.exists(slot_4_path):
                os.remove(slot_4_path)


if __name__ == "__main__":
    unittest.main()
