import math

import pygame

from classes.Reactor import Reactor
from settings import *


class Room:

  def __init__(
      self,
      name: str,
      rect: tuple[int, int, int, int],
      max_power: int = 3,
      is_enemy: bool = False,
  ) -> None:
    self.name: str = name
    self.rect: pygame.Rect = pygame.Rect(rect)
    self.max_power: int = max_power
    self.current_power: int = 0
    self.is_enemy: bool = is_enemy
    self.health: float = 100.0
    self.max_health: float = 100.0
    self.oxygen: float = 100.0  # FTL Sauerstoffsystem (0.0 bis 100.0)
    self.has_breach: bool = False  # Hüllenleck

  def effective_max_power(self) -> int:
    return max(0, math.floor(self.max_power * (self.health / self.max_health)))

  def add_power(self, reactor: Reactor) -> None:
    if (
        self.current_power < self.effective_max_power()
        and reactor.available_power > 0
    ):
      self.current_power += 1
      reactor.available_power -= 1

  def remove_power(self, reactor: Reactor) -> None:
    if self.current_power > 0:
      self.current_power -= 1
      reactor.available_power += 1

  def apply_damage(self, amount: float, reactor: Reactor) -> None:
    self.health = max(0.0, self.health - amount)
    # 30% Chance auf Hüllenleck
    import random
    if random.random() < 0.35:
        self.has_breach = True
    while self.current_power > self.effective_max_power():
      self.remove_power(reactor)

  def repair(self, amount: float) -> None:
    if self.has_breach:
        self.has_breach = False
        return
    self.health = min(self.max_health, self.health + amount)

  def update_oxygen(self, dt: float, connected_rooms: list["Room"] = None) -> None:
    """Updates oxygen levels for FTL oxygen system (SRS Kap. 5.1)."""
    # Sauerstoffverlust durch Hüllenleck oder Beschädigung
    if self.has_breach:
      self.oxygen = max(0.0, self.oxygen - 25.0 * dt)
    elif self.health < 40.0:
      self.oxygen = max(0.0, self.oxygen - 8.0 * dt)
    elif self.current_power > 0 or not self.is_enemy:
      self.oxygen = min(100.0, self.oxygen + 3.0 * dt)


    # Sauerstoffaustausch mit verbundenen Räumen bei offenen Türen
    if connected_rooms:
      for other in connected_rooms:
        avg_o2 = (self.oxygen + other.oxygen) / 2.0
        self.oxygen += (avg_o2 - self.oxygen) * 1.5 * dt

  def draw(self, surface: pygame.Surface) -> None:
    fill_col = COLOR_ENEMY_ROOM if self.is_enemy else COLOR_ROOM
    border_col = COLOR_ENEMY_BORDER if self.is_enemy else COLOR_BORDER

    # Sauerstoffmangel-Overlay (Vakuum / Erstickung)
    if self.oxygen < 30.0:
      fill_col = (40, 20, 35) if self.is_enemy else (20, 35, 55)

    pygame.draw.rect(surface, fill_col, self.rect)
    pygame.draw.rect(surface, border_col, self.rect, 2)

    font = pygame.font.SysFont(None, 18)
    surface.blit(
        font.render(self.name, True, (220, 220, 220)),
        (self.rect.x + 6, self.rect.y + 5),
    )

    # System-Gesundheitsbalken
    hp_ratio = self.health / self.max_health
    hp_color = COLOR_HP_GREEN if hp_ratio > 0.4 else COLOR_HP_RED
    pygame.draw.rect(
        surface,
        (30, 30, 30),
        (self.rect.x + 6, self.rect.y + 22, self.rect.width - 12, 4),
    )
    pygame.draw.rect(
        surface,
        hp_color,
        (
            self.rect.x + 6,
            self.rect.y + 22,
            int((self.rect.width - 12) * hp_ratio),
            4,
        ),
    )

    # Sauerstoffanzeige (O2: 100%)
    o2_color = (100, 200, 255) if self.oxygen > 40.0 else (255, 100, 100)
    o2_txt = font.render(f"O2:{int(self.oxygen)}%", True, o2_color)
    surface.blit(o2_txt, (self.rect.right - 44, self.rect.y + 5))

    # Hüllenleck Icon zeichnen (falls vorhanden)
    if self.has_breach:
        cx, cy = self.rect.centerx, self.rect.centery
        pygame.draw.circle(surface, (15, 15, 15), (cx, cy), 12)
        pygame.draw.circle(surface, (255, 50, 50), (cx, cy), 13, 2)
        b_font = pygame.font.SysFont(None, 14, bold=True)
        lbl = b_font.render("LECK", True, (255, 80, 80))
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))

    if not self.is_enemy:

      eff_max = self.effective_max_power()
      for i in range(self.max_power):
        if i < eff_max:
          color = (
              COLOR_POWER_ACTIVE
              if i < self.current_power
              else COLOR_POWER_OFF
          )
        else:
          color = COLOR_HP_RED
        pygame.draw.rect(
            surface,
            color,
            (self.rect.x + 6 + (i * 14), self.rect.bottom - 18, 10, 10),
        )

