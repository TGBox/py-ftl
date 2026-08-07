import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.Reactor import Reactor
from classes.Room import Room
from classes.ShieldSystem import ShieldSystem


class TestShieldsAndReactor(unittest.TestCase):

    def test_shield_recharge_and_blocking(self):
        shield = ShieldSystem()
        shield.update(0.1, powered_layers=2)
        shield.current_layers = 2
        self.assertEqual(shield.max_layers, 2)
        self.assertEqual(shield.current_layers, 2)

        # Attempt block
        blocked = shield.attempt_block()
        self.assertTrue(blocked)
        self.assertEqual(shield.current_layers, 1)

        # Recharge shield with 2 power (recharge time is 4.0s + hit delay 1.5s per layer)
        for _ in range(100):
            shield.update(0.1, powered_layers=2)

        self.assertEqual(shield.current_layers, 2)

    def test_shield_ion_lock(self):
        shield = ShieldSystem()
        shield.update(0.1, powered_layers=2)
        shield.current_layers = 0
        shield.lock_timer = 5.0

        # Update while ion locked
        shield.update(1.0, powered_layers=2)
        self.assertEqual(shield.current_layers, 0, "Shield should not recharge while ion locked.")
        self.assertLess(shield.lock_timer, 5.0)

    def test_reactor_power_management(self):
        reactor = Reactor(total_power=8)
        self.assertEqual(reactor.available_power, 8)

        room = Room("Schild", (60, 245, 90, 90), max_power=3)
        self.assertEqual(room.current_power, 0)

        # Add power
        room.add_power(reactor)
        self.assertEqual(room.current_power, 1)
        self.assertEqual(reactor.available_power, 7)

        # Remove power
        room.remove_power(reactor)
        self.assertEqual(room.current_power, 0)
        self.assertEqual(reactor.available_power, 8)

    def test_effective_max_power(self):
        room = Room("Waffen", (160, 245, 90, 90), max_power=3)
        self.assertEqual(room.effective_max_power(), 3)

        # Apply damage
        room.health = 50.0  # 50% HP
        self.assertEqual(room.effective_max_power(), 1)

        # Ion lock
        room.ion_timer = 4.0
        self.assertEqual(room.effective_max_power(), 0)


if __name__ == "__main__":
    unittest.main()
