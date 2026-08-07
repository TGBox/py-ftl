import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from managers.sound_manager import SoundManager


class TestSoundManager(unittest.TestCase):

    def setUp(self):
        self.sound = SoundManager()

    def test_sfx_cache_completeness(self):
        # Verify all SFX keys exist in cache
        expected_sfx = [
            "laser_fire", "missile_fire", "beam_fire", "flak_fire", "ion_fire", "ion_hit",
            "teleport", "cloak", "shield_hit", "shield_recharge", "hull_hit", "explosion",
            "click", "purchase", "jump", "alarm", "low_fuel", "crew_death", "repair",
            "door", "achievement", "victory", "game_over"
        ]
        for key in expected_sfx:
            self.assertIn(key, self.sound._cache, f"Missing SFX key: {key}")
            self.assertIsInstance(self.sound._cache[key], pygame.mixer.Sound)

    def test_music_tracks_generation(self):
        expected_bgm = ["bgm_menu", "bgm_explore", "bgm_combat", "bgm_boss"]
        for track in expected_bgm:
            self.assertIn(track, self.sound._music_tracks, f"Missing BGM track: {track}")
            self.assertIsInstance(self.sound._music_tracks[track], pygame.mixer.Sound)

    def test_play_and_stop_music(self):
        self.sound.play_music("bgm_menu")
        self.assertEqual(self.sound._current_track_name, "bgm_menu")

        self.sound.play_music("bgm_combat")
        self.assertEqual(self.sound._current_track_name, "bgm_combat")

        self.sound.stop_music()
        self.assertIsNone(self.sound._current_track_name)

    def test_toggle_audio_and_music(self):
        self.assertTrue(self.sound.enabled)
        self.assertTrue(self.sound.music_enabled)

        # Toggle audio off
        self.sound.toggle()
        self.assertFalse(self.sound.enabled)
        self.assertFalse(self.sound.music_enabled)

        # Toggle audio back on
        self.sound.toggle()
        self.assertTrue(self.sound.enabled)


if __name__ == "__main__":
    unittest.main()
