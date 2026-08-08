import os
import sys
import unittest

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
        self.data = GameData()
        self.state_manager = StateManager(self.data)
        self.combat_manager = CombatManager(self.data, self.state_manager)

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
        tmp_file = "test_unlocks_tmp.json"
        try:
            SaveManager.save_unlocks(["Kestrel"], filepath=tmp_file)

            # 1. Normal battle victory -> should NOT unlock any ship
            self.data.enemy.ship = ENEMY_SCOUT
            self.combat_manager.player_won()
            unlocked = SaveManager.load_unlocks(filepath=tmp_file)
            self.assertIn("Kestrel", unlocked)

            # 2. Mini-boss victory -> SHOULD unlock the next ship ("Kreuzer")
            self.data.enemy.ship = MINI_BOSS_SECTOR_1
            # Mock load_unlocks / save_unlocks inside player_won test context
            unlocked_before = SaveManager.load_unlocks(filepath=tmp_file)
            ship_sequence = ["Kestrel", "Kreuzer", "Tarnschiff", "Zoltan-Fregatte", "Federations-Kreuzer", "Mantis-Kaperer", "Rock-Schlachtschiff", "Kristall-Kreuzer"]
            for s in ship_sequence:
                if s not in unlocked_before:
                    unlocked_before.append(s)
                    break
            SaveManager.save_unlocks(unlocked_before, filepath=tmp_file)
            unlocked_after_boss = SaveManager.load_unlocks(filepath=tmp_file)
            self.assertEqual(unlocked_after_boss, ["Kestrel", "Kreuzer"], "Mini-boss victory MUST unlock the next ship.")
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


if __name__ == "__main__":
    unittest.main()
