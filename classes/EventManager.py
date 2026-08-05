import random


class EventManager:

    def __init__(self) -> None:
        self.current_event_text: str = ""
        self.current_event_type: str | None = None
        self.choices: list[dict] = []

    def trigger_event(self, event_type: str, player_crew: list = None) -> tuple[int, int]:
        self.current_event_type = event_type
        self.choices.clear()
        has_engi = any(getattr(c, "species", "") == "Engi" for c in (player_crew or []))

        if event_type == "DISTRESS":
            self.current_event_text = "KEIN TREIBSTOFF MEHR! Die Notfall-Bake sendet ein Signal..."
            self.choices = []
            if has_engi:
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
            self.current_event_text = (
                f"Ein verlassenes Schiffswrack entdeckt! Fund: {scrap_found} Scrap, {fuel_found} Treibstoff."
            )
            self.choices = []
            if has_engi:
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

        elif event_type == "PLASMA_STORM":
            self.current_event_text = "ACHTUNG! Ein Plasma-Sturm stört die Schiffssysteme! Reaktor-Leistung halbfertig."
            self.choices = []
            if has_engi:
                self.choices.append({
                    "text": "[Engi-Spezial] Plasma-Energie absorbieren (+30 Scrap)",
                    "action": "CLAIM_RESOURCES",
                    "is_blue": True,
                    "scrap": 30,
                    "fuel": 1
                })
            self.choices.extend([
                {"text": "1. Nebel durchfliegen (+15 Scrap)", "action": "CLAIM_RESOURCES", "scrap": 15, "fuel": 0},
                {"text": "2. Umkehren & ausweichen", "action": "CONTINUE"}
            ])
            return 15, 0

        elif event_type == "ABANDONED_STATION":
            self.current_event_text = "Eine verlassene Raumstation treibt im All. Notsignale sind aktiv."
            self.choices = []
            if has_engi:
                self.choices.append({
                    "text": "[Engi-Spezial] Stationscomputer hacken (+25 Scrap, +2 Raketen)",
                    "action": "CLAIM_RESOURCES",
                    "is_blue": True,
                    "scrap": 25,
                    "fuel": 2
                })
            self.choices.extend([
                {"text": "1. Station durchsuchen (+20 Scrap)", "action": "CLAIM_RESOURCES", "scrap": 20, "fuel": 1},
                {"text": "2. Ignorieren & weiterfliegen", "action": "CONTINUE"}
            ])
            return 20, 1

        else:
            self.current_event_text = "Dieser Sektor ist ruhig. Keine ungewöhnlichen Aktivitäten gemeldet."
            self.choices = [
                {"text": "1. Weiterfliegen", "action": "CONTINUE"}
            ]
            return 0, 0

