import os
import sys
import unittest
from unittest.mock import MagicMock

from game import Game

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.Crew import Crew
from classes.GameData import GameData
from managers.shop_manager import ShopManager
from managers.training_manager import TrainingManager


class TestShopAndTraining(unittest.TestCase):

    def setUp(self):
        self.data = GameData()
        self.shop_manager = ShopManager(self.data)
        self.training_manager = TrainingManager(self.data)
        self.shop_manager.game = MagicMock()
        self.training_manager.game = MagicMock()

    def test_shop_catalog_generation(self):
        self.shop_manager.refresh_catalog()
        self.assertGreater(len(self.shop_manager.catalog_stock), 0)

    def test_shop_compatible_weapons_weighting(self):
        # Set player ship to a ship with specific slot restrictions (e.g. only ION and BEAM)
        self.data.player.ship.weapon_slots = [
            {"slot_id": 1, "allowed_types": ["ION"]},
            {"slot_id": 2, "allowed_types": ["BEAM"]},
        ]
        compatible_count = 0
        total_weapons_checked = 0

        for _ in range(100):
            self.shop_manager.refresh_catalog()
            weapons = [item for item in self.shop_manager.catalog_stock if item.get("type") != "AUGMENT"]
            for w in weapons:
                total_weapons_checked += 1
                if self.shop_manager.is_weapon_compatible(w):
                    compatible_count += 1

        ratio = compatible_count / total_weapons_checked
        # Around 90% should be compatible
        self.assertGreaterEqual(ratio, 0.75, f"Expected ~90% compatible weapons, got {ratio*100:.1f}%")

    def test_shop_buy_fuel_and_missiles(self):
        self.data.player.scrap = 100
        init_fuel = self.data.player.fuel
        init_missiles = self.data.player.missiles

        self.shop_manager.buy_fuel()
        self.assertEqual(self.data.player.fuel, init_fuel + 1)
        self.assertEqual(self.data.player.scrap, 97)

        self.shop_manager.buy_missiles()
        self.assertEqual(self.data.player.missiles, init_missiles + 3)
        self.assertEqual(self.data.player.scrap, 91)

    def test_shop_buy_hull_repair(self):
        self.data.player.scrap = 50
        self.data.player.ship.hp = 10

        self.shop_manager.buy_repair()
        self.assertEqual(self.data.player.ship.hp, 11)
        self.assertEqual(self.data.player.scrap, 48)

    def test_shop_insufficient_scrap(self):
        self.data.player.scrap = 1
        self.shop_manager.buy_fuel()
        self.assertEqual(self.data.player.scrap, 1)

    def test_training_manager_skill_upgrade(self):
        self.data.player.scrap = 100
        crew = Crew(100, 100, species="Mensch")
        self.data.player.crew = [crew]

        self.assertEqual(crew.skill_repair, 0)
        self.training_manager.buy_training(crew, "repair", "Reparatur")
        self.assertEqual(crew.skill_repair, 1)
        self.assertEqual(self.data.player.scrap, 80)


    def test_shop_buy_drone_parts(self):
        self.data.player.scrap = 50
        init_drones = getattr(self.data.player, "drone_parts", 5)
        self.shop_manager.buy_drone_parts()
        self.assertEqual(getattr(self.data.player, "drone_parts", 0), init_drones + 2)
        self.assertEqual(self.data.player.scrap, 44)

    def test_shop_reactor_upgrade_capping(self):
        self.data.player.scrap = 500
        max_needed = sum(r.max_power for r in self.data.player.ship.rooms)
        self.data.player.reactor.total_power = max_needed

        # Trying to upgrade reactor beyond max room power sum must be blocked
        self.shop_manager.upgrade_reactor()
        self.assertEqual(self.data.player.reactor.total_power, max_needed)

    def test_shop_crew_candidate_preview_and_purchase(self):
        self.data.player.scrap = 100
        cand = self.shop_manager.next_crew_candidate
        self.assertIsNotNone(cand)
        assert cand is not None
        self.assertIn("species", cand)

        initial_crew_count = len(self.data.player.crew)
        self.shop_manager.buy_crew()
        self.assertEqual(len(self.data.player.crew), initial_crew_count + 1)
        self.assertIsNotNone(self.shop_manager.next_crew_candidate)

    def test_shop_room_trading(self):
        from classes.Room import Room
        self.data.player.scrap = 200

        # Add a free room slot
        free_slot = Room("[Freier Raum-Slot]", (100, 100, 80, 80), max_power=0)
        self.data.player.ship.rooms.append(free_slot)

        # Buy system for free slot
        sys_item = {"name": "Tarnung", "desc": "Tarnung", "price": 80, "max_power": 3}
        self.shop_manager.buy_room_system(sys_item)
        self.assertEqual(free_room_installed := next(r for r in self.data.player.ship.rooms if r.name == "Tarnung").name, "Tarnung")

        # Sell optional system
        self.shop_manager.sell_room_system(free_slot)
        self.assertEqual(free_slot.name, "[Freier Raum-Slot]")

    def test_shop_weapon_overwrite_prevention(self):
        from classes.Weapon import Weapon
        self.data.player.scrap = 100
        w_laser = Weapon("Laser I", charge_time=3.0, w_type="LASER")
        self.data.player.weapons = [w_laser]

        missile_item = {"name": "Artemis Rakete", "charge_time": 4.0, "w_type": "MISSILE", "shield_pierce": 1, "damage": 40, "ammo_cost": 1, "price": 40}
        self.shop_manager.buy_weapon_to_slot(missile_item, 0)
        assert self.data.player.weapons[0] is not None
        self.assertEqual(self.data.player.weapons[0].w_type, "LASER")

    def test_empty_weapon_slot_rendering_and_save_handling(self):
        from managers.save_manager import SaveManager
        from managers.render_manager import RenderManager
        import pygame
        
        game = Game()
        self.data.player.weapons = [None, None]
        self.shop_manager.selecting_slot_item = {"name": "Laser I", "w_type": "LASER"}

        screen = pygame.Surface((960, 540))
        render_mgr = RenderManager(screen, self.data)

        # Must render slot selection without throwing AttributeError on NoneType
        render_mgr.draw_shop()

        # Must save game without throwing AttributeError on NoneType
        tmp_file = "test_save_tmp.dat"
        try:
            SaveManager.save_game(self.data, game, filepath=tmp_file)
        finally:
            import os
            if os.path.exists(tmp_file):
                os.remove(tmp_file)


if __name__ == "__main__":
    unittest.main()


