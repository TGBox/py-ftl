import unittest
import pygame
from classes.GameData import GameData
from classes.ShipModel import (
    ENEMY_SCOUT, REBEL_PURSUER_S1, REBEL_PURSUER_S2,
    REBEL_PURSUER_S3, REBEL_PURSUER_S4, REBEL_PURSUER_S5
)
from classes.Crew import Crew
from classes.Room import Room
from classes.Door import Door
from managers.combat_manager import CombatManager
from managers.map_manager import MapManager
from managers.sound_manager import SoundManager
from settings import GameState


class TestQoLAndBalancing(unittest.TestCase):

    def setUp(self):
        pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.data = GameData()
        self.sound = SoundManager()
        self.combat = CombatManager(self.data)
        self.combat.sound = self.sound
        self.map_mgr = MapManager(self.data)

    def test_quick_door_controls(self):
        r1 = Room("Brücke", (100, 100, 80, 80))
        r2 = Room("Antrieb", (200, 100, 80, 80))
        self.data.player.ship.rooms = [r1, r2]

        d1 = Door(r1, r2, (180, 130, 20, 20), is_airlock=False)
        d2 = Door(r2, None, (280, 130, 20, 20), is_airlock=False)
        d_air = Door(r1, None, (100, 90, 20, 20), is_airlock=True)
        self.data.player.ship.doors = [d1, d2, d_air]

        self.combat.open_all_doors()
        self.assertTrue(d1.is_open)
        self.assertTrue(d2.is_open)
        self.assertFalse(d_air.is_open)

        self.combat.close_all_doors()
        self.assertFalse(d1.is_open)
        self.assertFalse(d2.is_open)
        self.assertFalse(d_air.is_open)

    def test_crew_station_memory(self):
        r_bridge = Room("Brücke", (100, 100, 80, 80))
        r_engines = Room("Antrieb", (200, 100, 80, 80))
        self.data.player.ship.rooms = [r_bridge, r_engines]

        c1 = Crew(140, 140, name="Alice")
        c1.current_room = r_bridge
        c2 = Crew(240, 140, name="Bob")
        c2.current_room = r_engines
        self.data.player.crew = [c1, c2]

        self.combat.save_crew_stations()
        self.assertIn("Alice", self.combat.saved_crew_stations)
        self.assertIn("Bob", self.combat.saved_crew_stations)
        self.assertEqual(self.combat.saved_crew_stations["Alice"][:2], (140.0, 140.0))

        c1.x, c1.y = 50.0, 50.0
        c2.x, c2.y = 60.0, 60.0

        self.combat.return_crew_to_stations()
        self.assertEqual(c1.target_pos, (140, 140))
        self.assertEqual(c2.target_pos, (240, 140))

    def test_dynamic_rebel_pursuer_scaling(self):
        self.data.world.star_map.sector = 1
        self.map_mgr.start_rebel_pursuit_combat()
        self.assertEqual(self.data.enemy.ship.name, "Rebellen-Aufklärer (S1)")
        self.assertEqual(self.data.enemy.ship.max_hp, 10)
        self.assertEqual(self.data.enemy.shield.max_layers, 1)

        self.data.world.star_map.sector = 3
        self.map_mgr.start_rebel_pursuit_combat()
        self.assertEqual(self.data.enemy.ship.name, "Rebellen-Bomber (S3)")
        self.assertEqual(self.data.enemy.ship.max_hp, 18)
        self.assertEqual(self.data.enemy.shield.max_layers, 2)

        self.data.world.star_map.sector = 5
        self.map_mgr.start_rebel_pursuit_combat()
        self.assertEqual(self.data.enemy.ship.name, "Flotten-Elite-Kreuzer (S5)")
        self.assertEqual(self.data.enemy.ship.max_hp, 28)
        self.assertEqual(self.data.enemy.shield.max_layers, 3)

    def test_boss_surge_timer_and_prewarning(self):
        self.data.current_state = GameState.COMBAT
        self.data.enemy.ship.name = "Flaggschiff"
        self.data.combat.boss_phase = 2
        self.data.combat.drone_surge_timer = 2.0
        self.combat.surge_warned = False

        self.combat.update(0.6)
        self.assertTrue(self.combat.surge_warned)
        self.assertAlmostEqual(self.data.combat.drone_surge_timer, 1.4, delta=0.05)

    def test_sound_manager_crossfade(self):
        self.sound.play_music("bgm_explore")
        self.assertEqual(self.sound._current_track_name, "bgm_explore")
        self.sound.play_music("bgm_combat")
        self.assertEqual(self.sound._current_track_name, "bgm_combat")


if __name__ == "__main__":
    unittest.main()
