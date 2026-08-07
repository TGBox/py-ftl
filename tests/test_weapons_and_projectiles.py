import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.Projectile import Projectile
from classes.Room import Room
from classes.Weapon import Weapon


class TestWeaponsAndProjectiles(unittest.TestCase):

    def test_weapon_properties(self):
        laser = Weapon("Heavy Laser", charge_time=3.5, w_type="HEAVY_LASER", damage=40.0)
        self.assertEqual(laser.w_type, "HEAVY_LASER")
        self.assertEqual(laser.damage, 40.0)
        self.assertFalse(laser.is_ready())

        laser.update(4.0, powered=True)
        self.assertTrue(laser.is_ready())

    def test_weapon_ammo_cost(self):
        missile = Weapon("Artemis Missile", charge_time=4.0, w_type="MISSILE", ammo_cost=1)
        self.assertEqual(missile.ammo_cost, 1)

    def test_projectile_movement(self):
        room = Room("Schild", (100, 100, 90, 90))
        proj = Projectile((0, 0), room.rect.center, target_room=room, is_player_shot=True, damage=20.0)
        self.assertTrue(proj.alive)

        # Move projectile towards target
        for _ in range(50):
            proj.update(0.1)

        self.assertFalse(proj.alive, "Projectile should reach target and deactivate.")

    def test_beam_intersected_rooms(self):
        r1 = Room("Schild", (60, 245, 90, 90))
        r2 = Room("Waffen", (160, 245, 90, 90))
        rooms = [r1, r2]

        beam_proj = Projectile((50, 290), (260, 290), target_room=r1, is_player_shot=True, w_type="BEAM")
        beam_proj.x = 260.0
        beam_proj.y = 290.0
        intersected = beam_proj.get_intersected_rooms(rooms)

        self.assertIn(r1, intersected)
        self.assertIn(r2, intersected)

    def test_projectile_status_effects(self):
        room = Room("Brücke", (260, 245, 90, 90))
        proj = Projectile(
            (0, 0), room.rect.center, target_room=room, is_player_shot=True,
            fire_chance=1.0, breach_chance=1.0, stun_duration=3.0, crew_damage=50.0
        )
        self.assertEqual(proj.fire_chance, 1.0)
        self.assertEqual(proj.breach_chance, 1.0)
        self.assertEqual(proj.stun_duration, 3.0)
        self.assertEqual(proj.crew_damage, 50.0)


if __name__ == "__main__":
    unittest.main()
