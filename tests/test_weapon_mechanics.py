import unittest

from classes.Crew import Crew
from classes.GameData import GameData
from classes.Projectile import Projectile
from classes.Room import Room
from classes.Weapon import Weapon
from managers.combat_manager import CombatManager
from managers.state_manager import StateManager


class TestWeaponMechanics(unittest.TestCase):

    def setUp(self):
        self.data = GameData()
        self.state_mgr = StateManager(self.data)
        self.combat_mgr = CombatManager(self.data, self.state_mgr)

    def test_limited_weapon_range_dissipates(self):
        # Create a projectile with limited max_range of 100.0
        start_pos = (100.0, 100.0)
        target_pos = (500.0, 100.0)
        room = self.data.enemy.ship.rooms[0]

        proj = Projectile(
            start_pos,
            target_pos,
            target_room=room,
            is_player_shot=True,
            damage=25.0,
            max_range=100.0,
        )

        # Update projectile for 0.5 seconds (speed ~400 -> dist ~200 > 100)
        proj.update(0.5)

        self.assertFalse(proj.alive)
        self.assertTrue(proj.out_of_range)

    def test_beam_weapon_line_hits_all_rooms_and_crew(self):
        r1 = Room("Waffen", (100, 100, 80, 80), is_enemy=True)
        r2 = Room("Schild", (190, 100, 80, 80), is_enemy=True)
        self.data.enemy.ship.rooms = [r1, r2]

        c1 = Crew(140, 140, name="Enemy1", is_enemy=True)
        c1.current_room = r1
        c2 = Crew(230, 140, name="Enemy2", is_enemy=True)
        c2.current_room = r2
        self.combat_mgr.enemy_crew = [c1, c2]

        # Beam firing line passing through r1 (100, 100) to r2 (250, 100)
        proj = Projectile(
            (110.0, 140.0),
            (250.0, 140.0),
            target_room=r1,
            is_player_shot=True,
            w_type="BEAM",
            damage=30.0,
            crew_damage=40.0,
        )

        # Move beam tip to target position to represent full beam length
        proj.x = proj.target_x
        proj.y = proj.target_y

        intersected = proj.get_intersected_rooms(self.data.enemy.ship.rooms)
        self.assertIn(r1, intersected)
        self.assertIn(r2, intersected)

        init_c1_hp = c1.hp
        init_c2_hp = c2.hp

        # Process hit
        self.combat_mgr.handle_player_hit(proj)

        # Both rooms took damage
        self.assertLess(r1.health, 100.0)
        self.assertLess(r2.health, 100.0)

        # Both crew members in crossed rooms took damage
        self.assertLess(c1.hp, init_c1_hp)
        self.assertLess(c2.hp, init_c2_hp)

    def test_missile_causes_crew_damage(self):
        from unittest.mock import patch
        r1 = Room("Waffen", (100, 100, 80, 80), is_enemy=True)
        self.data.enemy.ship.rooms = [r1]

        c1 = Crew(140, 140, name="Enemy1", is_enemy=True)
        c1.current_room = r1
        self.combat_mgr.enemy_crew = [c1]

        proj = Projectile(
            (10.0, 140.0),
            (140.0, 140.0),
            target_room=r1,
            is_player_shot=True,
            w_type="MISSILE",
            damage=40.0,
            crew_damage=35.0,
        )

        init_hp = c1.hp
        with patch("random.random", return_value=0.99):
            self.combat_mgr.handle_player_hit(proj)

        # Enemy crew member in target room took explosive missile damage
        self.assertEqual(c1.hp, init_hp - 35.0)


if __name__ == "__main__":
    unittest.main()
