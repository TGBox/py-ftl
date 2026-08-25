import unittest
import pygame

from classes.Crew import Crew
from classes.GameData import GameData
from managers.combat_manager import CombatManager
from managers.state_manager import StateManager
from utils import get_room_manning_bonus


class TestRoomManningBonuses(unittest.TestCase):

    def setUp(self):
        self.data = GameData()
        self.state_mgr = StateManager(self.data)
        self.combat_mgr = CombatManager(self.data)

    def test_manning_bonus_helper(self):
        # Unmanned
        self.assertEqual(get_room_manning_bonus("Waffen", 0)["multiplier"], 1.0)

        # 1 Crew
        self.assertEqual(get_room_manning_bonus("Waffen", 1)["multiplier"], 1.20)
        self.assertEqual(get_room_manning_bonus("Schild", 1)["multiplier"], 1.20)
        self.assertEqual(get_room_manning_bonus("Brücke", 1)["evasion"], 0.10)
        self.assertEqual(get_room_manning_bonus("Maschinen", 1)["evasion"], 0.05)
        self.assertEqual(get_room_manning_bonus("Medbay", 1)["multiplier"], 1.25)
        self.assertEqual(get_room_manning_bonus("Drohnen-Kontrolle", 1)["multiplier"], 1.15)

        # 2 Crew
        self.assertEqual(get_room_manning_bonus("Waffen", 2)["multiplier"], 1.35)
        self.assertEqual(get_room_manning_bonus("Schild", 2)["multiplier"], 1.35)
        self.assertEqual(get_room_manning_bonus("Brücke", 2)["evasion"], 0.15)
        self.assertEqual(get_room_manning_bonus("Maschinen", 2)["evasion"], 0.10)
        self.assertEqual(get_room_manning_bonus("Medbay", 2)["multiplier"], 1.50)
        self.assertEqual(get_room_manning_bonus("Drohnen-Kontrolle", 2)["multiplier"], 1.30)

    def test_weapon_charge_manning_levels(self):
        w_room = next((r for r in self.data.player.ship.rooms if r.name == "Waffen"), None)
        self.assertIsNotNone(w_room)

        # 0 Crew
        self.data.player.crew.clear()
        w_count_0 = len([c for c in self.data.player.crew if c.current_room == w_room])
        self.assertEqual(get_room_manning_bonus("Waffen", w_count_0)["multiplier"], 1.0)

        # 1 Crew
        c1 = Crew(100, 100, species="Mensch")
        c1.current_room = w_room
        self.data.player.crew.append(c1)
        w_count_1 = len([c for c in self.data.player.crew if c.current_room == w_room])
        self.assertEqual(get_room_manning_bonus("Waffen", w_count_1)["multiplier"], 1.20)

        # 2 Crew
        c2 = Crew(100, 100, species="Engi")
        c2.current_room = w_room
        self.data.player.crew.append(c2)
        w_count_2 = len([c for c in self.data.player.crew if c.current_room == w_room])
        self.assertEqual(get_room_manning_bonus("Waffen", w_count_2)["multiplier"], 1.35)

    def test_evasion_manning_levels(self):
        b_room = next((r for r in self.data.player.ship.rooms if r.name == "Brücke"), None)
        e_room = next((r for r in self.data.player.ship.rooms if r.name == "Maschinen"), None)
        if b_room:
            b_room.current_power = b_room.max_power = 1
        if e_room:
            e_room.current_power = e_room.max_power = 1

        self.data.player.crew.clear()

        # Unmanned bridge & engines
        ev_0 = self.combat_mgr.get_player_evasion()

        # 1 Pilot
        pilot1 = Crew(100, 100, species="Mensch")
        pilot1.current_room = b_room
        self.data.player.crew.append(pilot1)
        ev_1_pilot = self.combat_mgr.get_player_evasion()
        self.assertGreater(ev_1_pilot, ev_0)

        # Co-Pilot (2 Crew in Bridge)
        pilot2 = Crew(100, 100, species="Mensch")
        pilot2.current_room = b_room
        self.data.player.crew.append(pilot2)
        ev_2_pilots = self.combat_mgr.get_player_evasion()
        self.assertGreater(ev_2_pilots, ev_1_pilot)

    def test_power_ratio_scaling(self):
        w_room = next((r for r in self.data.player.ship.rooms if r.name == "Waffen"), None)
        assert w_room is not None
        w_room.max_power = 4
        w_room.current_power = 2  # 50% power

        # Manned with 1 crew (base 1.20) at 50% power => 1.20 * 0.5 = 0.60
        bonus_50 = get_room_manning_bonus("Waffen", 1, room=w_room)
        self.assertAlmostEqual(bonus_50["multiplier"], 0.60)

        # 0 power => 0.0 multiplier
        w_room.current_power = 0
        bonus_0 = get_room_manning_bonus("Waffen", 1, room=w_room)
        self.assertEqual(bonus_0["multiplier"], 0.0)


if __name__ == "__main__":
    unittest.main()
