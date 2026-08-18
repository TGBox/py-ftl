import os
import sys
import unittest
from unittest.mock import MagicMock

from game import Game

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.Crew import Crew
from classes.GameData import GameData
from classes.Projectile import Projectile
from classes.ShipModel import ENEMY_BOSS, ENEMY_SCOUT, MINI_BOSS_SECTOR_1
from classes.Weapon import Weapon
from managers.combat_manager import CombatManager, center_crew_in_rooms
from managers.save_manager import SaveManager
from managers.state_manager import StateManager
from settings import STATE_COMBAT, STATE_VICTORY


class TestCombatManager(unittest.TestCase):

    def setUp(self):
        self.game = Game()
        self.data = self.game.data
        self.state_manager = StateManager(self.data)
        self.combat_manager = CombatManager(self.data)
        self.combat_manager.game = MagicMock()
        self.state_manager.game = MagicMock()

    def test_crew_centering_at_combat_start(self):
        tarnung = self.data.player.ship.rooms[5]
        # Position crew off-center in room corner
        off_center = Crew(tarnung.rect.left + 2, tarnung.rect.top + 2, name="CornerCrew")
        self.data.player.crew.append(off_center)

        center_crew_in_rooms(self.data.player.crew, self.data.player.ship.rooms)
        self.assertEqual(off_center.x, float(tarnung.rect.centerx))
        self.assertEqual(off_center.y, float(tarnung.rect.centery))

    def test_weapon_charging_and_firing(self):
        weapon = Weapon("Test Laser", charge_time=2.0, w_type="LASER")
        self.assertFalse(weapon.is_ready())

        weapon.update(2.5, powered=True)
        self.assertTrue(weapon.is_ready())

        weapon.reset()
        self.assertFalse(weapon.is_ready())

    def test_projectile_hits_and_damage(self):
        room = self.data.enemy.ship.rooms[0]
        init_hp = self.data.enemy.ship.hp
        room_init_hp = room.health

        proj = Projectile((100, 100), room.rect.center, target_room=room, is_player_shot=True, damage=25.0)

        # Force hit processing
        self.combat_manager.handle_player_hit(proj)
        self.assertLess(self.data.enemy.ship.hp, init_hp)
        self.assertLess(room.health, room_init_hp)

    def test_ship_unlock_rules(self):
        from unittest.mock import patch
        tmp_file = "test_unlocks_tmp.json"
        try:
            SaveManager.save_unlocks(["Kestrel"], filepath=tmp_file)

            with patch("managers.save_manager.SaveManager.load_unlocks", return_value=["Kestrel"]), \
                 patch("managers.save_manager.SaveManager.save_unlocks") as mock_save:

                # 1. Normal battle victory -> should NOT unlock any ship
                self.data.combat.combat_won = False
                self.data.world.star_map.sector = 2
                self.data.enemy.ship = ENEMY_SCOUT
                self.combat_manager.player_won()
                mock_save.assert_not_called()

                # 2. Mini-boss victory in Sector 2 -> should NOT unlock any ship
                self.data.combat.combat_won = False
                self.data.enemy.ship = MINI_BOSS_SECTOR_1
                self.combat_manager.player_won()
                mock_save.assert_not_called()

                # 3. Final boss victory in Sector 5 -> MUST unlock the next ship ("Kreuzer")
                self.data.combat.combat_won = False
                self.data.world.star_map.sector = 5
                self.data.enemy.ship = ENEMY_BOSS
                self.data.enemy.ship.name = "Flaggschiff"
                self.combat_manager.player_won()
                mock_save.assert_called_once_with(["Kestrel", "Kreuzer"])
        finally:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

    def test_boss_phase_transitions(self):
        self.data.enemy.ship = ENEMY_BOSS
        self.data.enemy.ship.name = "Flaggschiff"
        self.data.enemy.ship.hp = 0
        self.data.combat.boss_phase = 1

        self.combat_manager.check_end_of_battle()
        self.assertEqual(self.data.combat.boss_phase, 2)
        self.assertGreater(self.data.enemy.ship.hp, 0)

    def test_repair_drone_update_zero_dt_no_crash(self):
        self.data.combat.repair_drone_active = True
        drone_room = next((r for r in self.data.player.ship.rooms if r.name == "Drohnen-Kontrolle"), None)
        if drone_room:
            drone_room.current_power = 2
        target_room = self.data.player.ship.rooms[0]
        # Position repair drone exactly at target room center (dist = 0.0)
        self.data.combat.repair_drone_pos = (float(target_room.rect.centerx), float(target_room.rect.centery))

        # Call update with dt = 0.0 (simulating pause or zero dt)
        self.combat_manager.update(0.0)
        self.assertEqual(self.data.combat.repair_drone_pos, (float(target_room.rect.centerx), float(target_room.rect.centery)))

    def test_ftl_charging_and_fleeing(self):
        from settings import STATE_COMBAT, STATE_MAP
        self.data.current_state = STATE_COMBAT
        b_room = next((r for r in self.data.player.ship.rooms if r.name == "Brücke"), None)
        self.assertIsNotNone(b_room)
        assert b_room is not None
        b_room.max_power = 1
        b_room.current_power = 1
        b_room.health = 100.0

        self.data.player.crew.clear()
        pilot = Crew(float(b_room.rect.centerx), float(b_room.rect.centery), species="Mensch")
        pilot.current_room = b_room
        self.data.player.crew.append(pilot)

        # FTL should charge 10s
        self.combat_manager.update(10.0)
        self.assertAlmostEqual(self.data.combat.ftl_charge_timer, 10.0)
        self.assertFalse(self.data.combat.ftl_ready)

        # Charge remaining 20s => 30s total => ready
        self.combat_manager.update(20.0)
        self.assertEqual(self.data.combat.ftl_charge_timer, 30.0)
        self.assertTrue(self.data.combat.ftl_ready)

        # Fleeing combat should switch state to MAP
        from settings import STATE_MAP
        self.combat_manager.flee_combat()
        self.assertEqual(self.data.current_state, STATE_MAP)

    def test_post_combat_phase(self):
        from settings import STATE_COMBAT, STATE_MAP
        self.data.current_state = STATE_COMBAT
        self.data.enemy.ship.hp = 0

        self.combat_manager.check_end_of_battle()

        # Should stay in COMBAT state during post-combat phase
        self.assertEqual(self.data.current_state, STATE_COMBAT)
        self.assertTrue(self.data.combat.combat_won)

        # Leaving post-combat should transition to MAP
        self.combat_manager.leave_post_combat()
        self.assertEqual(self.data.current_state, STATE_MAP)
        self.assertFalse(self.data.combat.combat_won)

    def test_post_victory_update_loop_does_not_repeat_rewards(self):
        from settings import STATE_COMBAT
        self.data.current_state = STATE_COMBAT
        self.data.enemy.ship.hp = 0
        initial_scrap = self.data.player.scrap
        initial_sector = self.data.world.star_map.sector

        # First update triggers victory and gives rewards once
        self.combat_manager.update(0.1)
        scrap_after_win = self.data.player.scrap
        self.assertTrue(self.data.combat.combat_won)
        self.assertGreater(scrap_after_win, initial_scrap)

        # Subsequent updates (post-combat loop) must NOT award scrap or increment sector again
        for _ in range(10):
            self.combat_manager.update(0.1)

        self.assertEqual(self.data.player.scrap, scrap_after_win, "Scrap must not increase continuously during post-combat loop!")
        self.assertEqual(self.data.world.star_map.sector, initial_sector, "Sector must not increment repeatedly on every frame!")

    def test_combat_system_reset_between_battles(self):
        # Set active drones and cloaking
        self.data.combat.combat_drone_active = True
        self.data.combat.repair_drone_active = True
        self.data.combat.cloak_active_timer = 5.0

        # Reset combat systems via state manager
        self.state_manager.reset_combat_systems()

        self.assertFalse(self.data.combat.combat_drone_active)
        self.assertFalse(self.data.combat.repair_drone_active)
        self.assertEqual(self.data.combat.cloak_active_timer, 0.0)

    def test_faction_enemy_ship_variety(self):
        from managers.map_manager import MapManager
        map_mgr = MapManager(self.data)

        # Test Nebel sector spawns Zoltan or Drone Carrier or Scout
        self.data.world.star_map.sector_type = "Nebel-Sektor"
        map_mgr.start_normal_combat()
        self.assertIn(self.data.enemy.ship.name, ["Scout", "Zoltan-Fregatte", "Drohnen-Träger"])

        # Test Piraten sector spawns Mantis, Rock, or Bomber
        self.data.world.star_map.sector_type = "Piraten-Sektor"
        map_mgr.start_normal_combat()
        self.assertIn(self.data.enemy.ship.name, ["Mantis-Kaperer", "Rock-Kriegsschiff", "Kaper-Bomber"])

    def test_combat_options_overlay_state_preservation(self):
        from enums import GameState
        # Enter combat state
        self.state_manager.change_state(GameState.COMBAT)
        self.data.combat.combat_drone_active = True
        self.assertEqual(self.data.current_state, GameState.COMBAT.value)

        # Open Options Menu during combat
        self.state_manager.change_state(GameState.OPTIONS)
        self.assertEqual(self.data.current_state, GameState.OPTIONS.value)
        # Active combat drones should NOT be reset when entering Options
        self.assertTrue(self.data.combat.combat_drone_active)

        # Return from Options menu
        self.state_manager.return_from_overlay()
        self.assertEqual(self.data.current_state, GameState.COMBAT.value)
    def test_combat_victory_cleanup_and_drone_deactivation(self):
        self.data.combat.combat_drone_active = True
        self.data.combat.repair_drone_active = True
        self.combat_manager.enemy_crew_spawned = True

        self.combat_manager.player_won()

        self.assertTrue(self.data.combat.combat_won)
        self.assertFalse(self.data.combat.combat_drone_active)
        self.assertFalse(self.data.combat.repair_drone_active)
        self.assertFalse(self.combat_manager.enemy_crew_spawned)
        self.assertEqual(len(self.data.player.projectiles), 0)
        self.assertEqual(len(self.data.combat.weapon_targets), 0)

    def test_new_combat_reset_prevents_autowin(self):
        from enums import GameState
        self.data.combat.combat_won = True
        self.combat_manager.enemy_crew_spawned = False
        self.combat_manager.enemy_crew = []

        self.state_manager.change_state(GameState.COMBAT)

        self.assertFalse(self.data.combat.combat_won)
        self.assertFalse(self.combat_manager.enemy_crew_spawned)
        # Check end of battle must not trigger auto-win when enemy_crew is empty before spawning
        self.combat_manager.check_end_of_battle()
        self.assertFalse(self.data.combat.combat_won)


if __name__ == "__main__":
    unittest.main()



