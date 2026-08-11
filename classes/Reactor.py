import pygame

from settings import *

class Reactor:

  def __init__(self, total_power: int = 6) -> None:
    self.total_power: int = total_power
    self.available_power: int = total_power

  def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
    surface.blit(
        get_font(22).render(
            f"Reaktor: {self.available_power}/{self.total_power}",
            True,
            (200, 220, 255),
        ),
        (x, y),
    )
    for i in range(self.total_power):
      color = COLOR_REACTOR if i < self.available_power else COLOR_POWER_OFF
      pygame.draw.rect(surface, color, (x + i * 18, y + 25, 14, 25))
      
  def __str__(self) -> str:
    """Methode um eine gut lesbare String Repräsentation dieses Objektes zu erstellen.

    Returns:
        str: Die String Darstellung des Reaktor Objekts.
    """
    r_str = f"Reaktor - Verfügbare Power: {self.available_power} / Totale Power: {self.total_power}"
    return r_str