import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.Crew import Crew
from classes.GameData import GameData
from managers.achievement_manager import AchievementManager


class TestAchievements(unittest.TestCase):

    def setUp(self):
        self.tmp_file = "test_achievements_tmp.json"
        self.mgr = AchievementManager(self.tmp_file)

    def tearDown(self):
        if os.path.exists(self.tmp_file):
            os.remove(self.tmp_file)

    def test_achievement_initialization(self):
        self.assertEqual(len(self.mgr.achievements), 22, "AchievementManager should manage 22 achievements.")
        self.assertIn("first_victory", self.mgr.achievements)
        self.assertIn("flagship_down", self.mgr.achievements)
        self.assertFalse(self.mgr.achievements["first_victory"]["unlocked"])

    def test_unlock_and_persistence(self):
        # Unlock first victory
        unlocked = self.mgr.unlock("first_victory")
        self.assertTrue(unlocked)
        self.assertTrue(self.mgr.achievements["first_victory"]["unlocked"])
        self.assertEqual(len(self.mgr.toasts), 1)

        # Unlock again should return False
        self.assertFalse(self.mgr.unlock("first_victory"))

        # Load from disk into new manager
        loaded_mgr = AchievementManager(self.tmp_file)
        self.assertTrue(loaded_mgr.achievements["first_victory"]["unlocked"])
        self.assertFalse(loaded_mgr.achievements["boss_slayer"]["unlocked"])

    def test_toast_notifications(self):
        self.mgr.unlock("first_victory")
        self.assertEqual(len(self.mgr.toasts), 1)
        self.assertEqual(self.mgr.toasts[0]["timer"], 4.0)

        # Update toasts
        self.mgr.update_toasts(2.0)
        self.assertEqual(self.mgr.toasts[0]["timer"], 2.0)

        self.mgr.update_toasts(2.5)
        self.assertEqual(len(self.mgr.toasts), 0, "Toast should expire after timer reaches 0.")

    #def test_gamedata_integration(self):
    #    data = GameData()
    #    self.assertIsNotNone(data.achievement_manager)
#
    #    # Test skill level 3 unlock
    #    crew = Crew(100, 100, species="Engi")
    #    crew.train_skill("repair", data.achievement_manager)
    #    crew.train_skill("repair", data.achievement_manager)
    #    crew.train_skill("repair", data.achievement_manager)
#
    #    self.assertTrue(data.achievement_manager.achievements["master_mechanic"]["unlocked"])


if __name__ == "__main__":
    unittest.main()
