import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.Crew import Crew
from classes.EventManager import EventManager


class TestEventManager(unittest.TestCase):

    def setUp(self):
        self.event_manager = EventManager()

    def test_events_json_loading(self):
        self.assertGreater(len(self.event_manager.events_db), 0, "events.json must be loaded successfully.")

    def test_distress_out_of_fuel(self):
        crew = [Crew(100, 100, species="Engi")]
        self.event_manager.trigger_event("DISTRESS", crew, player_fuel=0)

        self.assertIn("KEIN TREIBSTOFF MEHR", self.event_manager.current_event_text)
        self.assertGreater(len(self.event_manager.choices), 0)

    def test_distress_with_fuel(self):
        crew = [Crew(100, 100, species="Engi")]
        self.event_manager.trigger_event("DISTRESS", crew, player_fuel=5)

        self.assertNotIn("KEIN TREIBSTOFF MEHR", self.event_manager.current_event_text)
        self.assertGreater(len(self.event_manager.choices), 0)

    def test_blue_choices_filtering(self):
        # Crew without Engi
        human_crew = [Crew(100, 100, species="Mensch")]
        self.event_manager.trigger_event("RESOURCE", human_crew, player_fuel=5)
        engi_choices = [c for c in self.event_manager.choices if c.get("requires_species") == "Engi"]
        self.assertEqual(len(engi_choices), 0, "Choices requiring Engi should be hidden when no Engi crew is present.")

        # Crew with Engi
        engi_crew = [Crew(100, 100, species="Engi")]
        self.event_manager.trigger_event("RESOURCE", engi_crew, player_fuel=5)
        # Verify choices can be loaded
        self.assertGreater(len(self.event_manager.choices), 0)

    def test_all_event_types(self):
        crew = [Crew(100, 100, species="Engi"), Crew(100, 100, species="Mantis")]
        for ev_type in ["RESOURCE", "NEBULA", "EMPTY", "COMBAT", "SHOP"]:
            self.event_manager.trigger_event(ev_type, crew, player_fuel=5)
            self.assertGreater(len(self.event_manager.choices), 0, f"Event type {ev_type} should generate choices.")

    def test_risky_event_outcomes_and_consequences(self):
        from unittest.mock import patch
        from classes.GameData import PlayerData
        from classes.ShipModel import ShipModel
        p_data = PlayerData()
        p_data.ship = ShipModel(name="Kestrel", max_hp=30, rooms=[])
        p_data.crew = [Crew(100, 100, species="Mensch")]

        # Trigger station fire event
        self.event_manager.trigger_event("DISTRESS", p_data.crew, player_fuel=5)
        # Find distress_station_fire in matching events
        station_fire_event = [e for e in self.event_manager.events_db if e.get("id") == "distress_station_fire"][0]
        self.event_manager.choices = station_fire_event.choices

        # Test failure branch (roll = 0.99 > 0.35)
        with patch("random.random", return_value=0.99):
            self.event_manager.select_choice(0, p_data)
            self.assertEqual(p_data.ship.hp, 24) # 30 - 6 damage
            self.assertEqual(p_data.crew[0].hp, 70) # 100 - 30 crew_damage
            self.assertIn("FEHLSCHLAG", self.event_manager.result_text)

        # Test success branch (roll = 0.10 <= 0.35)
        p_data.ship.hp = 30
        p_data.crew[0].hp = 100
        init_scrap = p_data.scrap
        self.event_manager.choices = station_fire_event.choices
        with patch("random.random", return_value=0.10):
            self.event_manager.select_choice(0, p_data)
            self.assertEqual(p_data.ship.hp, 30)
            self.assertEqual(p_data.scrap, init_scrap + 40)
            self.assertIn("ERFOLG", self.event_manager.result_text)


if __name__ == "__main__":
    unittest.main()
