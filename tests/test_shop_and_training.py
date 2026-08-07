import os
import sys
import unittest

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


if __name__ == "__main__":
    unittest.main()
