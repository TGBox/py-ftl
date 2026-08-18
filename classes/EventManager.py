import json
import os
import random
from typing import Any, Optional

from classes.Crew import Crew
from classes.Event import Event, EventChoice
from classes.GameData import PlayerData


class EventManager:

    def __init__(self, json_path: str = "data/events.json") -> None:
        self.current_event_text: str = ""
        self.current_event_type: str | None = None
        self.result_text: str = ""
        self.choices: list[EventChoice] = []
        self.events_db: list[Event] = []
        self.pending_action: str | None = None
        self.load_events_json(json_path)
        
    def __str__(self) -> str:
        """Methode um aus dem EventManager Objekt eine von Menschen gut lesbare String Repräsentation zu generieren.

        Returns:
            str: Die String Repräsentation des EventManager Objekts.
        """
        e_str = f"EventTyp: {self.current_event_type} - EventText: \"{self.current_event_text}\"\n"
        e_str += f"Ergebnistext: \"{self.result_text}\"\n{len(self.choices)} Choices:\n"
        for i, c in enumerate(self.choices):
            if i != len(self.choices) -1:
                e_str += f"{c}, "
            else:
                e_str += f"{c}\n"
        e_str += f"{len(self.events_db)} EventsDB:\n"
        for i, e in enumerate(self.events_db):
            if i != len(self.events_db) -1:
                e_str += f"{e}, \n"
            else:
                e_str += f"{e}\n"
        e_str += f"Ausstehende Aktion: {self.pending_action}"
        return e_str

    def load_events_json(self, json_path: str) -> None:
        paths_to_check = [json_path, "events.json", "data/events.json"]
        for p in paths_to_check:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        raw_events = data.get("events", [])
                        self.events_db = [Event.from_dict(e) for e in raw_events]
                        print(f"Geladene Events: {len(self.events_db)}")
                        return
                except Exception as e:
                    print(f"Fehler beim Laden von {p}: {e}")

    def select_choice(self, choice_idx: int, player_data: Optional[PlayerData] = None) -> str:
        """Verarbeitet die gewählte Option, setzt den Resultat-Text und führt Aktionen aus."""
        from classes.GameData import PlayerData
        if choice_idx < 0 or choice_idx >= len(self.choices):
            return "CONTINUE"
        
        choice: EventChoice = self.choices[choice_idx]
        # Unterstützt zufällige Outcomes (Erfolg/Fehlschlag mit Wahrscheinlichkeit)
        outcomes: list[dict[str, Any]] | None = choice.get("outcomes")
        if outcomes:
            roll = random.random()
            cumulative = 0.0
            chosen_outcome = outcomes[-1]
            for outcome in outcomes:
                cumulative += float(outcome.get("chance", 1.0))
                if roll <= cumulative:
                    chosen_outcome = outcome
                    break
            choice = EventChoice.from_dict(chosen_outcome)

        # Resultat-Text für das UI setzen
        self.result_text = str(choice.get("result_text", "Aktion erfolgreich ausgeführt."))
        action = str(choice.get("action", "CONTINUE"))
            
        if isinstance(player_data, PlayerData):
            # Spieler-Ressourcen/Schaden anpassen, falls übergeben
            if player_data:
                if "scrap" in choice:
                    player_data.scrap = max(0, player_data.scrap + int(choice["scrap"]))
                if "fuel" in choice:
                    player_data.fuel = max(0, player_data.fuel + int(choice["fuel"]))
                if "missiles" in choice:
                    player_data.missiles = max(0, player_data.missiles + int(choice["missiles"]))
                if "drones" in choice or "drone_parts" in choice:
                    d_val = int(choice.get("drones", choice.get("drone_parts", 0)))
                    player_data.drone_parts = max(0, getattr(player_data, "drone_parts", 5) + d_val)
                if "damage" in choice and hasattr(player_data, "ship") and player_data.ship:
                    player_data.ship.hp = max(0, player_data.ship.hp - int(choice["damage"]))

            self.pending_action = action
            self.choices = []
        return action

    def trigger_event(
        self, event_type: str, player_crew: list[Crew] | None = None, player_fuel: int = 1
    ) -> tuple[int, int]:
        self.current_event_type = event_type
        self.choices.clear()
        self.result_text = ""
        crew_species = [getattr(c, "species", "") for c in (player_crew or [])]

        # Wenn Treibstoff leer (<=0) und DISTRESS-Event -> Echte Treibstoff-Notfallbake!
        if event_type == "DISTRESS" and player_fuel <= 0:
            self.current_event_text = "KEIN TREIBSTOFF MEHR! Die Notfall-Bake sendet ein Signal..."
            if "Engi" in crew_species:
                self.choices.append(EventChoice.from_dict({
                    "text": "[Engi-Spezial] Notfall-Reaktor modifizieren (+2 Treibstoff)",
                    "action": "SCAVENGE_FUEL",
                    "fuel": 2,
                    "is_blue": True
                }))
            self.choices.extend([
                EventChoice.from_dict({"text": "1. Händler rufen (-10 Scrap für 2 Treibstoff)", "action": "BUY_FUEL"}),
                EventChoice.from_dict({"text": "2. Wrack scavengen (+1 Treibstoff)", "action": "SCAVENGE_FUEL", "fuel": 1}),
            ])
            return 0, 0

        # Finde passende Events aus events.json (case-insensitive machen zur Sicherheit)
        matching = [
            e for e in self.events_db 
            if str(e.get("event_type", "")).upper() == str(event_type).upper()
        ]
        if matching:
            event_def = random.choice(matching)
            self.current_event_text = event_def.get("text", "")
            raw_choices = event_def.get("choices", [])

            for ch in raw_choices:
                ch_obj = EventChoice.from_dict(ch)
                req = ch_obj.requires_species
                if req and req not in crew_species:
                    continue  # Spezies-Voraussetzung nicht erfüllt -> ausblenden
                self.choices.append(ch_obj)
            return 0, 0

        # Fallback Standard-Events falls keine in events.json matchten
        if event_type == "DISTRESS":
            self.current_event_text = "KEIN TREIBSTOFF MEHR! Die Notfall-Bake sendet ein Signal..."
            if "Engi" in crew_species:
                self.choices.append(EventChoice.from_dict({
                    "text": "[Engi-Spezial] Notfall-Reaktor modifizieren (+2 Treibstoff)",
                    "action": "SCAVENGE_FUEL",
                    "is_blue": True
                }))
            self.choices.extend([
                EventChoice.from_dict({"text": "1. Händler rufen (-10 Scrap für 2 Treibstoff)", "action": "BUY_FUEL"}),
                EventChoice.from_dict({"text": "2. Wrack scavengen (+1 Treibstoff)", "action": "SCAVENGE_FUEL"}),
            ])
            return 0, 0

        elif event_type == "RESOURCE":
            scrap_found = random.randint(10, 25)
            fuel_found = random.randint(1, 2)
            self.current_event_text = f"Ein verlassenes Schiffswrack entdeckt! Fund: {scrap_found} Scrap, {fuel_found} Treibstoff."
            if "Engi" in crew_species:
                self.choices.append(EventChoice.from_dict({
                    "text": "[Engi-Spezial] Bauteile optimal verwerten (+35 Scrap, +3 Fuel)",
                    "action": "CLAIM_RESOURCES",
                    "is_blue": True,
                    "scrap": 35,
                    "fuel": 3
                }))
            self.choices.append(
                EventChoice.from_dict({"text": "1. Beute einsammeln & weiterreisen", "action": "CLAIM_RESOURCES", "scrap": scrap_found, "fuel": fuel_found})
            )
            return scrap_found, fuel_found

        elif event_type == "COMBAT":
            self.current_event_text = "WARNUNG! Ein feindliches Piratenschiff nähert sich!"
            self.choices = [
                EventChoice.from_dict({"text": "1. Gefecht starten!", "action": "START_COMBAT"}),
                EventChoice.from_dict({"text": "2. Ausweichen & entkommen", "action": "FLEE"}),
            ]
            return 0, 0

        elif event_type == "SHOP":
            self.current_event_text = "Willkommen an der Händler-Station!"
            self.choices = [
                EventChoice.from_dict({"text": "1. Shop betreten", "action": "ENTER_SHOP"})
            ]
            return 0, 0
        
        elif event_type == "NEBULA":
            self.current_event_text = "Ihr trefft in dichten Nebelwolken auf treibende Reste."
            self.choices = [EventChoice.from_dict({"text": "1. Nebel durchkunden", "action": "CONTINUE"})]
            return 0, 0

        elif event_type == "EMPTY":
            self.current_event_text = "Dieser Sektorpunkt ist ruhig und leer."
            self.choices = [EventChoice.from_dict({"text": "1. Weiterfliegen", "action": "CONTINUE"})]
            return 0, 0

        else:
            self.current_event_text = "Dieser Sektor ist ruhig. Keine ungewöhnlichen Aktivitäten gemeldet."
            self.choices = [
                EventChoice.from_dict({"text": "1. Weiterfliegen", "label": "1. Weiterfliegen", "action": "CONTINUE"})
            ]
            return 0, 0