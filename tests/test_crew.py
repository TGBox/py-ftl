import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import pygame

# Path setup to ensure module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.Crew import Crew, find_room_path
from classes.ShipModel import PLAYER_SHIP


class TestCrew(unittest.TestCase):

    def setUp(self):
        self.ship = PLAYER_SHIP
        self.rooms = self.ship.rooms
        self.doors = self.ship.doors

    def test_crew_initialization_and_species_traits(self):
        engi = Crew(100, 100, species="Engi")
        self.assertEqual(engi.species, "Engi")
        self.assertGreater(engi.repair_multiplier, 1.0)
        self.assertLess(engi.melee_multiplier, 1.0)

        mantis = Crew(100, 100, species="Mantis")
        self.assertEqual(mantis.species, "Mantis")
        self.assertGreater(mantis.melee_multiplier, 1.0)

        human = Crew(100, 100, species="Mensch")
        self.assertEqual(human.species, "Mensch")

    def test_skill_training(self):
        crew = Crew(100, 100, species="Mensch")
        # Train repair 3 times
        self.assertTrue(crew.train_skill("repair"))
        self.assertTrue(crew.train_skill("repair"))
        self.assertTrue(crew.train_skill("repair"))
        self.assertFalse(crew.train_skill("repair"))  # Cannot train beyond lvl 3
        self.assertEqual(crew.skill_repair, 3)

        # Train fitness 3 times
        init_hp = crew.max_hp
        self.assertTrue(crew.train_skill("fitness"))
        self.assertGreater(crew.max_hp, init_hp)

    def test_bfs_pathfinding(self):
        tarnung = next(r for r in self.rooms if r.name == "Tarnung")
        bruecke = next(r for r in self.rooms if r.name == "Brücke")

        path = find_room_path(tarnung, bruecke, self.rooms, self.doors)
        self.assertGreater(len(path), 0)

        crew = Crew(tarnung.rect.centerx, tarnung.rect.centery, name="Tester")
        crew.target_pos = (bruecke.rect.centerx, bruecke.rect.centery)
        crew.recalculate_path(self.rooms, self.doors)

        self.assertGreater(len(crew.path_waypoints), 0)
        self.assertEqual(crew.path_waypoints[-1], (float(bruecke.rect.centerx), float(bruecke.rect.centery)))

    def test_door_auto_open_and_close(self):
        tarnung = next(r for r in self.rooms if r.name == "Tarnung")
        bruecke = next(r for r in self.rooms if r.name == "Brücke")

        crew = Crew(tarnung.rect.centerx, tarnung.rect.centery)
        crew.target_pos = (bruecke.rect.centerx, bruecke.rect.centery)

        dt = 0.1
        opened_door = None
        for _ in range(250):
            crew.update(dt, self.rooms, self.doors)
            self.ship.update_doors(dt, [crew])
            for d in self.doors:
                if d.opened_by_crew and not opened_door:
                    opened_door = d

        self.assertIsNotNone(opened_door, "Crew should automatically open doors while passing through.")
        assert opened_door is not None
        self.assertFalse(opened_door.is_open, "Door should automatically close behind crew after moving away.")

    def test_room_damage_and_healing(self):
        from classes.GameData import GameData
        from managers.combat_manager import CombatManager

        data = GameData()
        cm = CombatManager(data)
        cm.game = MagicMock()

        medbay = next(r for r in data.player.ship.rooms if r.name == "Medbay")
        medbay.current_power = 2

        crew = Crew(medbay.rect.centerx, medbay.rect.centery)
        crew.hp = 50.0
        crew.current_room = medbay
        data.player.crew = [crew]

        # Update combat manager crew processing
        cm.update_crew(0.5)
        self.assertGreater(crew.hp, 50.0, "Crew inside powered Medbay should heal over time during combat updates.")


    @patch("pygame.mouse.get_pos")  # <- Geändert
    def test_crew_corner_offsets_in_same_room(self, mock_get_pos):
        from classes.GameData import GameData
        from managers.input_manager import InputManager

        data = GameData()
        from settings import STATE_COMBAT
        data.current_state = STATE_COMBAT
        
        # 1. Verhindere, dass der Klick als "Entern" auf dem Gegnerschiff gewertet wird
        data.enemy.ship.rooms.clear()

       # 2. Nutze den ersten Raum des Spielerschiffs als Ziel
        room = data.player.ship.rooms[0]

        # 3. Crew in einen anderen Raum platzieren, damit das Pathfinding funktioniert
        start_room = data.player.ship.rooms[1]
        c1 = Crew(start_room.rect.centerx, start_room.rect.centery)
        c2 = Crew(start_room.rect.centerx, start_room.rect.centery)
        c1.selected = True
        c2.selected = True
        c1.is_boarding = False
        c2.is_boarding = False
        data.player.crew = [c1, c2]

        input_mgr = InputManager(data)
        # WICHTIG: Auf None belassen!
        input_mgr.game = None  
        
        # 4. Pygame Mausposition mocken
        mock_get_pos.return_value = (room.rect.centerx, room.rect.centery)

        input_mgr.handle_left_click(
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                pos=(room.rect.centerx, room.rect.centery),
                button=1,
            )
        )

        # 5. Assertions prüfen
        self.assertIsNotNone(c1.target_pos, "Klick kam nicht bei der Crew an!")
        self.assertIsNotNone(c2.target_pos)
        self.assertNotEqual(c1.target_pos, c2.target_pos, "Crew in same room must be assigned opposing corner offsets!")

    def test_targeting_cancel_esc_and_right_click(self):
        from classes.GameData import GameData
        from managers.input_manager import InputManager
        from settings import STATE_COMBAT
        import pygame

        data = GameData()
        data.current_state = STATE_COMBAT
        data.combat.is_targeting = True
        data.combat.target_weapon_idx = 0

        input_mgr = InputManager(data)
        input_mgr.game = MagicMock()

        # Simulate ESC key
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        input_mgr.handle_keydown(esc_event)
        self.assertFalse(data.combat.is_targeting, "ESC must cancel weapon targeting mode.")

        # Simulate Right-Click
        data.combat.is_targeting = True
        rc_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(100, 100))
        input_mgr.handle_right_click(rc_event)
        self.assertFalse(data.combat.is_targeting, "Right-Click must cancel weapon targeting mode.")


if __name__ == "__main__":
    unittest.main()