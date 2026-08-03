import random


class EventManager:

  def __init__(self) -> None:
    self.current_event_text: str = ""
    self.current_event_type: str | None = None

  def trigger_event(self, event_type: str) -> tuple[int, int]:
    self.current_event_type = event_type
    if event_type == "RESOURCE":
      scrap_found = random.randint(10, 25)
      fuel_found = random.randint(1, 2)
      self.current_event_text = (
          f"Wrack untersucht! Fund: {scrap_found} Scrap, {fuel_found}"
          " Treibstoff."
      )
      return scrap_found, fuel_found
    elif event_type == "COMBAT":
      self.current_event_text = (
          "WARNUNG! Ein feindliches Piratenschiff greift an!"
      )
      return 0, 0
    elif event_type == "SHOP":
      self.current_event_text = (
          "Willkommen an der Händler-Station! Bereit zum Handeln."
      )
      return 0, 0
    else:
      self.current_event_text = (
          "Dieser Sektor ist ruhig. Keine Aktivitäten gemeldet."
      )
      return 0, 0