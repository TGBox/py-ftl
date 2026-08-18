import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game import Game
from settings import *


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
        lx, ly = self.game.render_manager._logical_mouse_pos(for_overlay=True) # type: ignore
        self.assertIsInstance(lx, int)
        self.assertIsInstance(ly, int)

    def test_modal_overlay_z_index_hover_suppression(self):
        self.game.screen = pygame.Surface((960, 540))
        render_mgr = self.game.render_manager

        # Without overlays, _logical_mouse_pos returns valid coordinates
        self.game.data.show_pause_menu = False
        self.assertFalse(render_mgr.is_any_overlay_active)
        lx, ly = render_mgr._logical_mouse_pos(for_overlay=False)
        self.assertNotEqual((lx, ly), (-9999, -9999))

        # With pause menu overlay active, _logical_mouse_pos(for_overlay=False) returns (-9999, -9999)
        self.game.data.show_pause_menu = True
        self.assertTrue(render_mgr.is_any_overlay_active)
        lx, ly = render_mgr._logical_mouse_pos(for_overlay=False)
        self.assertEqual((lx, ly), (-9999, -9999))

        # But for_overlay=True returns real logical coordinates
        lx_ov, ly_ov = render_mgr._logical_mouse_pos(for_overlay=True)
        self.assertNotEqual((lx_ov, ly_ov), (-9999, -9999))

    def test_modal_overlay_click_lock(self):
        from enums import GameState
        input_mgr = self.game.input_manager
        door = self.game.data.player.ship.doors[0]
        initial_open = door.is_open

        # When show_pause_menu is True, clicking door coordinate should be ignored
        self.game.data.show_pause_menu = True
        self.game.data.current_state = GameState.MAP.value
        mock_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(door.rect.centerx, door.rect.centery))
        input_mgr.handle_left_click(mock_event)
        self.assertEqual(door.is_open, initial_open)

        # When in STATE_TRAINING, top bar or door clicks are ignored
        self.game.data.show_pause_menu = False
        self.game.data.current_state = GameState.TRAINING.value
        input_mgr.handle_left_click(mock_event)
        self.assertEqual(door.is_open, initial_open)


if __name__ == "__main__":
    unittest.main()
