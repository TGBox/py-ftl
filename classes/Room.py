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
    while self.current_power > self.effective_max_power():
      self.remove_power(reactor)

  def repair(self, amount: float) -> None:
    self.health = min(self.max_health, self.health + amount)

  def draw(self, surface: pygame.Surface) -> None:
    fill_col = COLOR_ENEMY_ROOM if self.is_enemy else COLOR_ROOM
    border_col = COLOR_ENEMY_BORDER if self.is_enemy else COLOR_BORDER
    pygame.draw.rect(surface, fill_col, self.rect)
    pygame.draw.rect(surface, border_col, self.rect, 2)

    font = pygame.font.SysFont(None, 20)
    surface.blit(
        font.render(self.name, True, (220, 220, 220)),
        (self.rect.x + 6, self.rect.y + 6),
    )

    # System-Gesundheitsbalken
    hp_ratio = self.health / self.max_health
    hp_color = COLOR_HP_GREEN if hp_ratio > 0.4 else COLOR_HP_RED
    pygame.draw.rect(
        surface,
        (30, 30, 30),
        (self.rect.x + 6, self.rect.y + 24, self.rect.width - 12, 5),
    )
    pygame.draw.rect(
        surface,
        hp_color,
        (
            self.rect.x + 6,
            self.rect.y + 24,
            int((self.rect.width - 12) * hp_ratio),
            5,
        ),
    )

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
            (self.rect.x + 6 + (i * 14), self.rect.bottom - 20, 10, 12),
        )
