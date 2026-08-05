import random


class EventManager:

    def __init__(self) -> None:
        self.current_event_text: str = ""
        self.current_event_type: str | None = None
        self.choices: list[dict] = []

    def trigger_event(self, event_type: str) -> tuple[int, int]:
        self.current_event_type = event_type
        self.choices.clear()

        if event_type == "DISTRESS":
            self.current_event_text = "KEIN TREIBSTOFF MEHR! Die Notfall-Bake sendet ein Signal..."
            self.choices = [
                {"text": "1. Händler rufen (-10 Scrap für 2 Treibstoff)", "action": "BUY_FUEL"},
                {"text": "2. Wrack scavengen (+1 Treibstoff)", "action": "SCAVENGE_FUEL"},
            ]
            return 0, 0

        elif event_type == "RESOURCE":
            scrap_found = random.randint(10, 25)
            fuel_found = random.randint(1, 2)
            self.current_event_text = (
                f"Ein verlassenes Schiffswrack entdeckt! Fund: {scrap_found} Scrap, {fuel_found} Treibstoff."
            )
            self.choices = [
                {"text": "1. Beute einsammeln & weiterreisen", "action": "CLAIM_RESOURCES", "scrap": scrap_found, "fuel": fuel_found}
            ]
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