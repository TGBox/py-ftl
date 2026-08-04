import math

import pygame

from classes.Room import Room
from settings import COLOR_PROJECTILE


class Projectile:

  def __init__(
      self,
      start_pos: tuple[int, int],
      target_pos: tuple[int, int],
      target_room: Room,
      is_player_shot: bool,
  ) -> None:
    self.x: float = float(start_pos[0])
    self.y: float = float(start_pos[1])
    self.target_x: float = float(target_pos[0])
    self.target_y: float = float(target_pos[1])
    self.target_room: Room = target_room
    self.is_player_shot: bool = is_player_shot
    self.alive: bool = True

    dx = self.target_x - self.x
    dy = self.target_y - self.y
    dist = math.hypot(dx, dy)
    self.vx: float = (dx / dist) * 400.0 if dist != 0 else 0.0
    self.vy: float = (dy / dist) * 400.0 if dist != 0 else 0.0

  def update(self, dt: float) -> None:
    self.x += self.vx * dt
    self.y += self.vy * dt
    if math.hypot(self.target_x - self.x, self.target_y - self.y) < 10:
      self.alive = False

  def draw(self, surface: pygame.Surface) -> None:
    pygame.draw.circle(
        surface, COLOR_PROJECTILE, (int(self.x), int(self.y)), 5
    )