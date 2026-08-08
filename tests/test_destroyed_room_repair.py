import unittest

from classes.Reactor import Reactor
from classes.Room import Room


class TestDestroyedRoomRepair(unittest.TestCase):

    def test_enemy_destroyed_room_5x_repair_penalty(self):
        enemy_room = Room("Waffen", (100, 100, 80, 80), is_enemy=True)
        reactor = Reactor()

        # Damaged partially (e.g. 50 HP damage) -> was_destroyed stays False
        enemy_room.apply_damage(50.0, reactor)
        enemy_room.has_breach = False
        enemy_room.fire_level = 0.0
        self.assertEqual(enemy_room.health, 50.0)
        self.assertFalse(enemy_room.was_destroyed)

        # Repair 10 HP -> at normal speed (amount = 10 -> health = 60)
        enemy_room.repair(10.0)
        self.assertEqual(enemy_room.health, 60.0)

        # Now completely destroy room (health -> 0)
        enemy_room.apply_damage(100.0, reactor)
        enemy_room.has_breach = False
        enemy_room.fire_level = 0.0
        self.assertEqual(enemy_room.health, 0.0)
        self.assertTrue(enemy_room.was_destroyed)

        # Repair 10 HP -> 5x slowdown (effective_amount = 10 / 5 = 2 HP)
        enemy_room.repair(10.0)
        self.assertEqual(enemy_room.health, 2.0)
        self.assertTrue(enemy_room.was_destroyed)

        # Repair back to max (490 HP repair input -> 490/5 = 98 HP -> 2 + 98 = 100 max)
        enemy_room.repair(490.0)
        self.assertEqual(enemy_room.health, 100.0)
        self.assertFalse(enemy_room.was_destroyed)

    def test_player_room_normal_repair(self):
        player_room = Room("Waffen", (100, 100, 80, 80), is_enemy=False)
        reactor = Reactor()

        # Destroy player room
        player_room.apply_damage(100.0, reactor)
        player_room.has_breach = False
        player_room.fire_level = 0.0
        self.assertEqual(player_room.health, 0.0)

        # Player rooms are repaired at normal speed (10 HP repair input -> 10 HP health)
        player_room.repair(10.0)
        self.assertEqual(player_room.health, 10.0)


if __name__ == "__main__":
    unittest.main()
