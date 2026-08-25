import os
import sys
import unittest
import pygame

from game import Game

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.Crew import Crew
from classes.GameData import GameData
from managers.combat_manager import CombatManager
from managers.state_manager import StateManager


class TestCrewAbilities(unittest.TestCase):

    def setUp(self):
        self.data = GameData()
        self.state_mgr = StateManager(self.data)
        self.combat_mgr = CombatManager(self.data)
        self.game = Game()

    def test_engi_overclock_instant_repair(self):
        engi = Crew(150, 150, name="Slockat", species="Engi")
        room = self.data.player.ship.rooms[0]
        room.health = 50.0
        room.fire_level = 30.0
        room.has_breach = True
        engi.current_room = room

        success = engi.activate_ability(self.data, self.game, self.combat_mgr)
        self.assertTrue(success, "Engi ability activation should succeed.")
        self.assertEqual(room.health, 85.0, "Engi ability should restore +35 HP.")
        self.assertEqual(room.fire_level, 0.0, "Engi ability should extinguish fire.")
        self.assertFalse(room.has_breach, "Engi ability should seal breaches.")
        self.assertGreater(engi.ability_cooldown, 0.0, "Engi ability should enter cooldown.")

    def test_mantis_frenzy_melee_multiplier(self):
        mantis = Crew(150, 150, name="Kazaak", species="Mantis")
        mantis.trait = "Sprinter"
        mantis.melee_multiplier = 2.0
        self.assertEqual(mantis.melee_multiplier, 2.0)

        success = mantis.activate_ability(self.data, self.game, self.combat_mgr)
        self.assertTrue(success)

        # Update crew for 0.1s
        mantis.update(0.1, self.data.player.ship.rooms)
        self.assertEqual(mantis.melee_multiplier, 4.0, "Mantis Frenzy should double melee damage multiplier to 4.0.")

    def test_rock_earthquake_stuns_enemies(self):
        rock = Crew(150, 150, name="Boulder", species="Rock")
        room = self.data.player.ship.rooms[0]
        rock.current_room = room

        enemy_boarder = Crew(155, 155, name="Enemy", species="Mantis", is_enemy=True)
        enemy_boarder.current_room = room
        self.combat_mgr.enemy_crew.append(enemy_boarder)

        success = rock.activate_ability(self.data, self.game, self.combat_mgr)
        self.assertTrue(success)
        self.assertEqual(enemy_boarder.stun_timer, 4.0, "Rock earthquake should stun enemy boarders in room for 4.0s.")

    def test_zoltan_shield_burst(self):
        zoltan = Crew(150, 150, name="Kael", species="Zoltan")
        self.data.player.shield.current_layers = 0

        success = zoltan.activate_ability(self.data, self.game, self.combat_mgr)
        self.assertTrue(success)
        self.assertEqual(self.data.player.shield.current_layers, 1, "Zoltan Shield Burst should restore 1 shield layer.")

    def test_human_tactical_focus_heals_allies(self):
        human = Crew(150, 150, name="Marcus", species="Mensch")
        ally = Crew(155, 155, name="Elena", species="Mensch")
        room = self.data.player.ship.rooms[0]
        human.current_room = room
        ally.current_room = room
        ally.hp = 50.0
        self.data.player.crew.extend([human, ally])

        success = human.activate_ability(self.data, self.game, self.combat_mgr)
        self.assertTrue(success)
        self.assertEqual(ally.hp, 75.0, "Human Tactical Focus should heal allies in room by +25 HP.")


if __name__ == "__main__":
    unittest.main()
