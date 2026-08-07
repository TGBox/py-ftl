import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from managers.particle_manager import ParticleManager


class TestParticleManager(unittest.TestCase):

    def setUp(self):
        self.mgr = ParticleManager()

    def test_emit_explosion(self):
        self.assertEqual(len(self.mgr.particles), 0)
        self.mgr.emit_explosion(200, 200, count=30)
        self.assertGreater(len(self.mgr.particles), 30)

    def test_emit_shield_ripple(self):
        self.mgr.emit_shield_ripple(300, 300, color=(0, 200, 255), count=16)
        self.assertEqual(len(self.mgr.particles), 16)

    def test_emit_sparks_and_thruster(self):
        self.mgr.emit_sparks(100, 100, count=10)
        self.assertEqual(len(self.mgr.particles), 10)

        self.mgr.emit_thruster(50, 50, direction_x=-1.0)
        self.assertEqual(len(self.mgr.particles), 11)

    def test_particle_physics_and_decay(self):
        self.mgr.emit_sparks(100, 100, count=5)
        initial_count = len(self.mgr.particles)

        # Fast forward time by 2.0s (all sparks have life < 0.5s)
        self.mgr.update(2.0)
        self.assertEqual(len(self.mgr.particles), 0, "Expired particles should be automatically cleaned up.")

    def test_particle_draw_does_not_crash(self):
        self.mgr.emit_explosion(200, 200, count=15)
        surf = pygame.Surface((900, 600))
        try:
            self.mgr.draw(surf)
        except Exception as e:
            self.fail(f"ParticleManager.draw raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
