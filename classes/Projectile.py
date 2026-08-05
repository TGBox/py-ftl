import math

import pygame

from classes.Room import Room
from settings import COLOR_PROJECTILE


class Projectile:

  def __init__(
      self,
      start_pos: tuple[float, float],
      target_pos: tuple[float, float],
      target_room: Room,
      is_player_shot: bool,
      w_type: str = "LASER",
      shield_pierce: int = 0,
      damage: float = 35.0,
  ) -> None:
    self.x: float = float(start_pos[0])
    self.y: float = float(start_pos[1])
    self.target_x: float = float(target_pos[0])
    self.target_y: float = float(target_pos[1])
    self.target_room: Room = target_room
    self.is_player_shot: bool = is_player_shot
    self.w_type: str = w_type
    self.shield_pierce: int = shield_pierce
    self.damage: float = damage
    self.alive: bool = True

    dx = self.target_x - self.x
    dy = self.target_y - self.y
    dist = math.hypot(dx, dy)
    speed = 600.0 if w_type == "BEAM" else 400.0
    self.vx: float = (dx / dist) * speed if dist != 0 else 0.0
    self.vy: float = (dy / dist) * speed if dist != 0 else 0.0

  def update(self, dt: float) -> None:
    self.x += self.vx * dt
    self.y += self.vy * dt
    if math.hypot(self.target_x - self.x, self.target_y - self.y) < 10:
      self.alive = False

  def get_intersected_rooms(self, rooms: list[Room]) -> list[Room]:
    """Prüft per Liniensegment-Schnittpunkt, welche Räume vom Beam gekreuzt werden (SRS Kap. 6.2)."""
    intersected = []
    for room in rooms:
        if room.rect.clipline((self.x, self.y), (self.target_x, self.target_y)):
            intersected.append(room)
    return intersected if intersected else [self.target_room]

  def draw(self, surface: pygame.Surface) -> None:
    if self.w_type == "MISSILE":
      pygame.draw.rect(
          surface, (255, 140, 0), (int(self.x) - 4, int(self.y) - 4, 8, 8)
      )
    elif self.w_type == "BEAM":
      pygame.draw.line(
          surface, (255, 255, 100), (int(self.x), int(self.y)), (int(self.target_x), int(self.target_y)), 3
      )
      pygame.draw.circle(
          surface, (255, 255, 100), (int(self.x), int(self.y)), 7
      )
    else:  # LASER
      pygame.draw.circle(
          surface, COLOR_PROJECTILE, (int(self.x), int(self.y)), 5
      )