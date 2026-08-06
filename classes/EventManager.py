import json
import os
import random


class EventManager:

    def __init__(self, json_path: str = "data/events.json") -> None:
        self.current_event_text: str = ""
        self.current_event_type: str | None = None
        self.result_text: str = ""
        self.choices: list[dict] = []
        self.events_db: list[dict] = []
        self.load_events_json(json_path)

    def load_events_json(self, json_path: str) -> None:
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.events_db = data.get("events", [])
            except Exception as e:
                print(f"Fehler beim Laden von {json_path}: {e}")

    def trigger_event(self, event_type: str, player_crew: list = None) -> tuple[int, int]:
        self.current_event_type = event_type
        self.choices.clear()
        self.result_text = ""
        crew_species = [getattr(c, "species", "") for c in (player_crew or [])]

        # Finde passende Events aus events.json
        matching = [e for e in self.events_db if e.get("event_type") == event_type]
        if matching:
            event_def = random.choice(matching)
            self.current_event_text = event_def.get("text", "")
            raw_choices = event_def.get("choices", [])

            for ch in raw_choices:
                req = ch.get("requires_species")
                if req and req not in crew_species:
                    continue  # Erfülle Spezies-Voraussetzung nicht -> ausblenden
                self.choices.append(ch)
            return 0, 0

        # Fallback Standard-Events falls keine in events.json matchten
        if event_type == "DISTRESS":
            self.current_event_text = "KEIN TREIBSTOFF MEHR! Die Notfall-Bake sendet ein Signal..."
            if "Engi" in crew_species:
                self.choices.append({
                    "text": "[Engi-Spezial] Notfall-Reaktor modifizieren (+2 Treibstoff)",
                    "action": "SCAVENGE_FUEL",
                    "is_blue": True
                })
            self.choices.extend([
                {"text": "1. Händler rufen (-10 Scrap für 2 Treibstoff)", "action": "BUY_FUEL"},
                {"text": "2. Wrack scavengen (+1 Treibstoff)", "action": "SCAVENGE_FUEL"},
            ])
            return 0, 0

        elif event_type == "RESOURCE":
            scrap_found = random.randint(10, 25)
            fuel_found = random.randint(1, 2)
            self.current_event_text = f"Ein verlassenes Schiffswrack entdeckt! Fund: {scrap_found} Scrap, {fuel_found} Treibstoff."
            if "Engi" in crew_species:
                self.choices.append({
                    "text": "[Engi-Spezial] Bauteile optimal verwerten (+35 Scrap, +3 Fuel)",
                    "action": "CLAIM_RESOURCES",
                    "is_blue": True,
                    "scrap": 35,
                    "fuel": 3
                })
            self.choices.append(
                {"text": "1. Beute einsammeln & weiterreisen", "action": "CLAIM_RESOURCES", "scrap": scrap_found, "fuel": fuel_found}
            )
            return scrap_found, fuel_found

        elif event_type == "COMBAT":
            self.current_event_text = "WARNUNG! Ein feindliches Piratenschiff nähert sich!"
            self.choices = [
                {"text": "1. Gefecht starten!", "action": "START_COMBAT"},
                {"text": "2. Ausweichen & entkommen", "action": "FLEE"},
            ]
            return 0, 0

        elif event_type == "SHOP":
            self.current_event_text = "Willkommen an der Händler-Station!"
            self.choices = [
                {"text": "1. Shop betreten", "action": "ENTER_SHOP"}
            ]
            return 0, 0

        else:
            self.current_event_text = "Dieser Sektor ist ruhig. Keine ungewöhnlichen Aktivitäten gemeldet."
            self.choices = [
                {"text": "1. Weiterfliegen", "action": "CONTINUE"}
            ]
            return 0, 0