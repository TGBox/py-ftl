import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.GameData import GameData
from classes.ShipModel import SHIP_BLUEPRINTS
from managers.render_manager import RenderManager


class TestFTLSprites(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def test_all_ship_sprite_files_exist(self):
        ship_names = ["Kestrel", "Kreuzer", "Tarnschiff", "Zoltan-Fregatte", "Federations-Kreuzer", "Mantis-Kaperer"]
        for name in ship_names:
            ship = SHIP_BLUEPRINTS[name]
            self.assertTrue(ship.hull_image, f"{name} should have a hull_image defined.")
            hull_path = os.path.join("assets", ship.hull_image)
            self.assertTrue(os.path.exists(hull_path), f"File {hull_path} should exist.")

            fp_path = os.path.join("assets", ship.floorplan_image)
            self.assertTrue(os.path.exists(fp_path), f"File {fp_path} should exist.")

    def test_render_manager_loads_ftl_sprites(self):
        screen = pygame.Surface((900, 600))
        data = GameData()
        render_mgr = RenderManager(screen, data)

        img = render_mgr.get_loaded_ship_sprite("ships/kestrel_a_hull.png", (400, 200), flip_x=False)
        self.assertIsNotNone(img, "RenderManager should successfully load kestrel_a_hull.png.")

        flipped_img = render_mgr.get_loaded_ship_sprite("ships/osprey_hull.png", (400, 200), flip_x=True)
        self.assertIsNotNone(flipped_img, "RenderManager should successfully load and flip osprey_hull.png.")

    def test_draw_combat_with_official_sprites_does_not_crash(self):
        screen = pygame.Surface((900, 600))
        data = GameData()
        data.current_state = "COMBAT"
        render_mgr = RenderManager(screen, data)

        try:
            render_mgr.draw_combat()
        except Exception as e:
            self.fail(f"draw_combat with official FTL ship sprites raised exception: {e}")


if __name__ == "__main__":
    unittest.main()
