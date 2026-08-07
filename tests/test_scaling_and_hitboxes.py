import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game import Game
from settings import LOGICAL_WIDTH, LOGICAL_HEIGHT


class TestScalingAndHitboxes(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_screen_to_logical_1920x1080(self):
        # Mock screen size 1920x1080
        self.game.screen = pygame.Surface((1920, 1080))

        # Test Top-Left corner of logical canvas
        # 1920x1080 aspect ratio matches 16:9, scale = 1.8, scaled_w = 1620, offset_x = 150
        lx, ly = self.game.screen_to_logical(150, 0)
        self.assertEqual((lx, ly), (0, 0))

        # Test Center of screen (960, 540) -> logical (450, 300)
        lx, ly = self.game.screen_to_logical(960, 540)
        self.assertEqual((lx, ly), (450, 300))

        # Test Bottom-Right of logical canvas (1770, 1080) -> logical (900, 600)
        lx, ly = self.game.screen_to_logical(1770, 1080)
        self.assertEqual((lx, ly), (900, 600))

    def test_screen_to_logical_ultrawide(self):
        # Mock Ultrawide 2560x1080 (21:9)
        self.game.screen = pygame.Surface((2560, 1080))
        # scale = 1.8, scaled_w = 1620, offset_x = (2560 - 1620) // 2 = 470
        lx, ly = self.game.screen_to_logical(470, 0)
        self.assertEqual((lx, ly), (0, 0))

        lx, ly = self.game.screen_to_logical(1280, 540)
        self.assertEqual((lx, ly), (450, 300))

    def test_render_manager_uses_logical_coordinates(self):
        self.game.screen = pygame.Surface((1920, 1080))
        # Verify render_manager._logical_mouse_pos returns scaled logical coordinates
        lx, ly = self.game.render_manager._logical_mouse_pos()
        self.assertIsInstance(lx, int)
        self.assertIsInstance(ly, int)


if __name__ == "__main__":
    unittest.main()
