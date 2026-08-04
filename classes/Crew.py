import math

import pygame

from classes.Room import Room
from settings import COLOR_CREW, COLOR_SELECTED


class Crew:

  def __init__(self, x: float, y: float) -> None:
    self.x: float = x
    self.y: float = y
    self.radius: int = 12
    self.selected: bool = False
    self.target_pos: tuple[int, int] | None = None

  def update(self, dt: float, rooms: list[Room]) -> None:
    if self.target_pos:
      tx, ty = self.target_pos
      dx, dy = tx - self.x, ty - self.y
      dist = math.hypot(dx, dy)
      if dist < 120.0 * dt:
        self.x, self.y = float(tx), float(ty)
        self.target_pos = None
      else:
        self.x += (dx / dist) * 120.0 * dt
        self.y += (dy / dist) * 120.0 * dt
    else:
      for room in rooms:
        if room.rect.collidepoint(int(self.x), int(self.y)):
          if room.health < room.max_health:
            room.repair(25.0 * dt)
          break

  def draw(self, surface: pygame.Surface) -> None:
    color = COLOR_SELECTED if self.selected else COLOR_CREW
    pygame.draw.circle(
        surface, color, (int(self.x), int(self.y)), self.radius
    )