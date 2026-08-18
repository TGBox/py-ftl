import unittest

from classes.GameData import GameData
from classes.Weapon import Weapon
from managers.shop_manager import ShopManager


class TestWeaponSlotSwap(unittest.TestCase):

    def setUp(self):
        self.data = GameData()
        self.shop_mgr = ShopManager(self.data)

    def test_swap_weapon_slots(self):
        ship = self.data.player.ship
        self.assertGreaterEqual(len(ship.weapon_slots), 2)

        # Set specific allowed_types for slots
        ship.weapon_slots[0]["allowed_types"] = ["LASER", "BEAM"]
        ship.weapon_slots[1]["allowed_types"] = ["MISSILE"]

        w1 = Weapon("Burst Laser", charge_time=8.0, w_type="LASER", damage=25.0, ammo_cost=0)
        w2 = Weapon("Artemis Missile", charge_time=10.0, w_type="MISSILE", damage=35.0, ammo_cost=1)
        self.data.player.weapons = [w1, w2]

        # Perform weapon slot swap
        success = ship.swap_weapon_slots(0, 1, self.data.player.weapons)
        self.assertTrue(success)

        # Verify allowed_types swapped
        self.assertEqual(ship.weapon_slots[0]["allowed_types"], ["MISSILE"])
        self.assertEqual(ship.weapon_slots[1]["allowed_types"], ["LASER", "BEAM"])

        # Verify equipped weapons swapped
        assert self.data.player.weapons[0] is not None
        self.assertEqual(self.data.player.weapons[0].name, "Artemis Missile")
        assert self.data.player.weapons[1] is not None
        self.assertEqual(self.data.player.weapons[1].name, "Burst Laser")

    def test_layout_swap_mode_toggle(self):
        self.data.player.scrap = 50
        self.shop_mgr.start_layout_swap()
        self.assertTrue(self.shop_mgr.layout_swap_mode)
        self.assertEqual(self.shop_mgr.layout_swap_type, "ROOMS")

        # Switch to WEAPONS tab
        self.shop_mgr.handle_layout_swap_click(450, 25)
        self.assertEqual(self.shop_mgr.layout_swap_type, "WEAPONS")


if __name__ == "__main__":
    unittest.main()
