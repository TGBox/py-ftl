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

        # Verify bought crew members in the spawn room sit at distinct corner positions
        spawn_room = self.data.player.ship.rooms[0]
        c1 = self.data.player.crew[0]
        c_last = self.data.player.crew[-1]
        self.assertNotEqual((c1.x, c1.y), (c_last.x, c_last.y), "Crew members in same room must spawn in distinct corner slots!")
        self.assertNotEqual((c_last.x, c_last.y), (spawn_room.rect.centerx, spawn_room.rect.centery), "Bought crew must not spawn dead-center when offset slots are available!")

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

    def test_shop_room_slot_display_and_counting(self):
        from classes.Room import Room
        # Ensure free room slots count matches
        free_rooms_before = [r for r in self.data.player.ship.rooms if r.name == "[Freier Raum-Slot]"]
        free_slot = Room("[Freier Raum-Slot]", (150, 150, 80, 80), max_power=0)
        self.data.player.ship.rooms.append(free_slot)

        free_rooms_after = [r for r in self.data.player.ship.rooms if r.name == "[Freier Raum-Slot]"]
        self.assertEqual(len(free_rooms_after), len(free_rooms_before) + 1)

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
        render_mgr.game = game
        #render_mgr.game.screen_to_logical.return_value = (0, 0)

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


    def test_shop_catalog_weapons_have_range(self):
        from managers.shop_manager import WEAPON_CATALOG_MASTER
        for w_item in WEAPON_CATALOG_MASTER:
            range_val = w_item.get("max_range")
            self.assertIsNotNone(range_val, f"Weapon '{w_item['name']}' in catalog master must have max_range set!")
            self.assertGreaterEqual(range_val, 750.0, f"Weapon '{w_item['name']}' max_range={range_val} must be at least 750.0 px!")


    def test_shop_buy_weapon_no_compatible_slot_prevention(self):
        from classes.Weapon import Weapon
        self.data.player.scrap = 200
        # Fill player slots with non-fusible weapons
        self.data.player.weapons = [
            Weapon("Artemis Rakete", charge_time=4.0, w_type="MISSILE"),
            Weapon("Pike Strahl", charge_time=5.0, w_type="BEAM"),
            Weapon("Ion Blast", charge_time=3.0, w_type="ION"),
        ]
        self.data.player.ship.max_weapons = 3
        self.data.player.ship.weapon_slots = [
            {"slot_id": 1, "allowed_types": ["MISSILE"]},
            {"slot_id": 2, "allowed_types": ["BEAM"]},
            {"slot_id": 3, "allowed_types": ["ION"]},
        ]

        # Trying to buy a LASER weapon when no slot allows LASER
        laser_item = {"name": "Standard Laser", "charge_time": 3.0, "w_type": "LASER", "price": 30}
        ok, reason = self.shop_manager.can_buy_weapon(laser_item)
        self.assertFalse(ok, "can_buy_weapon should return False when no slot allows LASER!")
        self.assertIn("KEIN PASSENDER ODER FREIER WAFFENSLOT", reason)

    def test_shop_inventory_randomness_on_enter_shop(self):
        from managers.map_manager import MapManager
        from unittest.mock import MagicMock
        map_mgr = MapManager(self.data)
        mock_game = MagicMock()
        mock_game.shop_manager = self.shop_manager
        map_mgr.game = mock_game

        # Trigger enter_shop
        map_mgr.enter_shop()

    def test_sell_crew_member(self):
        # Create 2 crew members
        c1 = Crew(0, 0, name="Alpha", species="Mensch")
        c2 = Crew(0, 0, name="Beta", species="Zoltan")
        c2.skill_repair = 2
        c2.skill_combat = 1
        self.data.player.crew = [c1, c2]

        # Verify price calculation: Zoltan base (30) + 3 skills * 5 = 45 Scrap
        price_c2 = self.shop_manager.calculate_crew_sell_price(c2)
        self.assertEqual(price_c2, 45)

        # Sell c2 (index 1)
        init_scrap = self.data.player.scrap
        self.shop_manager.sell_crew_at_idx(1)
        self.assertEqual(self.data.player.scrap, init_scrap + 45)
        self.assertEqual(len(self.data.player.crew), 1)

        # Try selling last remaining crew member (index 0) -> should be blocked!
        self.shop_manager.sell_crew_at_idx(0)
        self.assertEqual(len(self.data.player.crew), 1, "Selling last crew member must be blocked!")
        self.assertIn("MINDESTENS 1 CREW-MITGLIED", self.data.combat.msg)

    def test_mk5_fusion_max_level_prevention(self):
        from classes.Weapon import Weapon
        laser_mk5 = Weapon("Standard Laser", charge_time=3.0, w_type="LASER", level=5)
        self.data.player.weapons = [laser_mk5]
        self.data.player.scrap = 200

        item = {"name": "Standard Laser", "charge_time": 3.0, "w_type": "LASER", "price": 40}

        # Attempt to fuse level 5 weapon
        self.shop_manager.buy_weapon_to_slot(item, 0)

        self.assertEqual(self.data.player.weapons[0].level, 5, "Weapon level must remain capped at 5!")
        self.assertIn("MAXIMALES FUSION-LEVEL", self.data.combat.msg)

    def test_crew_training_compact_layout_scaling(self):
        # Create 6 crew members to test 6-crew compact training layout
        self.data.player.crew = [Crew(0, 0, name=f"Crew #{i+1}", species="Mensch") for i in range(6)]
        self.data.player.scrap = 200

        # Click upgrade button for 6th crew member (index 5) repair skill
        # card_y = 98 + 5 * 65 = 423
        # btn_x = 465 + 4 = 469, btn_y = 423 + 4 + 28 = 455
        self.training_manager.handle_click(475, 460)

        self.assertEqual(self.data.player.crew[5].skill_repair, 1)
        self.assertEqual(self.data.player.scrap, 180)

    def test_render_text_fitted(self):
        import pygame
        pygame.font.init()
        font = pygame.font.SysFont(None, 16)
        mock_surface = MagicMock()
        from managers.render_manager import RenderManager
        rm = RenderManager(mock_surface, self.data)

        long_text = "Erlaubt: LASER, BEAM, MISSILE | Reichweite: 600px"
        # Render fitted to narrow 100px width
        fitted_surf = rm.render_text_fitted(font, long_text, (255, 255, 255), 100)
        self.assertLessEqual(fitted_surf.get_width(), 100)

        # Render fitted to wide 500px width (should not truncate)
        full_surf = rm.render_text_fitted(font, long_text, (255, 255, 255), 500)
        self.assertEqual(full_surf.get_width(), font.render(long_text, True, (255, 255, 255)).get_width())


if __name__ == "__main__":
    unittest.main()


