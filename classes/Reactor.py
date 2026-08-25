import pygame

from settings import *

class Reactor:

  def __init__(self, total_power: int = 6) -> None:
    self.total_power: int = total_power
    self.available_power: int = total_power
    self.ion_storm_active: bool = False

  def get_effective_total_power(self) -> int:
    if self.ion_storm_active:
      return max(1, self.total_power // 2)
    return self.total_power

  def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
    eff_total = self.get_effective_total_power()
    cur_avail = max(0, min(self.available_power, eff_total))

    # Panel-Hintergrund
    panel_w = max(145, self.total_power * 16 + 15)
    panel_h = 58 if not self.ion_storm_active else 68
    panel_rect = pygame.Rect(x - 5, y - 5, panel_w, panel_h)
    panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel_surf.fill((14, 22, 38, 220))
    surface.blit(panel_surf, (panel_rect.x, panel_rect.y))
    pygame.draw.rect(surface, (0, 200, 255) if not self.ion_storm_active else (255, 140, 0), panel_rect, 1)

    # Titel & Status-Text
    title_color = (200, 230, 255) if not self.ion_storm_active else (255, 180, 80)
    title_txt = f"Reaktor: {cur_avail}/{eff_total}"
    if self.ion_storm_active:
      title_txt += " (Sturm)"
    lbl = get_font(15, bold=True).render(title_txt, True, title_color)
    surface.blit(lbl, (x, y))

    if self.ion_storm_active:
      sub = get_font(11).render("-50% Strom im Nebel", True, (255, 120, 80))
      surface.blit(sub, (x, y + 15))

    # Stromblöcke zeichnen
    block_y = y + 30 if self.ion_storm_active else y + 20
    for i in range(self.total_power):
      bx = x + (i % 8) * 16
      by = block_y + (i // 8) * 16
      if i >= eff_total:
        # Durch Nebel-Ion-Sturm deaktiviert
        pygame.draw.rect(surface, (100, 25, 25), (bx, by, 13, 13))
        pygame.draw.rect(surface, (255, 60, 60), (bx, by, 13, 13), 1)
      elif i < cur_avail:
        # Verfügbare freie Energie
        pygame.draw.rect(surface, COLOR_REACTOR, (bx, by, 13, 13))
        pygame.draw.rect(surface, (100, 255, 180), (bx, by, 13, 13), 1)
      else:
        # In Räumen belegt / verwendet
        pygame.draw.rect(surface, COLOR_POWER_OFF, (bx, by, 13, 13))
        pygame.draw.rect(surface, (70, 95, 125), (bx, by, 13, 13), 1)
      
  def __str__(self) -> str:
    """Methode um eine gut lesbare String Repräsentation dieses Objektes zu erstellen.

    Returns:
        str: Die String Darstellung des Reaktor Objekts.
    """
    r_str = f"Reaktor - Verfügbare Power: {self.available_power} / Totale Power: {self.total_power}"
    return r_str