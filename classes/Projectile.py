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
      subtype: str = "STANDARD",
      fire_chance: float = 0.0,
      breach_chance: float = 0.0,
      stun_duration: float = 0.0,
      crew_damage: float = 0.0,
  ) -> None:
    self.start_x: float = float(start_pos[0])
    self.start_y: float = float(start_pos[1])
    self.x: float = float(start_pos[0])
    self.y: float = float(start_pos[1])
    self.target_x: float = float(target_pos[0])
    self.target_y: float = float(target_pos[1])
    self.target_room: Room = target_room
    self.is_player_shot: bool = is_player_shot
    self.w_type: str = w_type
    self.shield_pierce: int = shield_pierce
    self.damage: float = damage
    self.subtype: str = subtype
    self.fire_chance: float = fire_chance
    self.breach_chance: float = breach_chance
    self.stun_duration: float = stun_duration
    self.crew_damage: float = crew_damage
    self.alive: bool = True

    dx = self.target_x - self.x
    dy = self.target_y - self.y
    dist = math.hypot(dx, dy)
    speed = 650.0 if w_type in ("BEAM", "BIO_BEAM") else (550.0 if w_type == "FLAK" else 400.0)
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
        if room.rect.clipline((self.start_x, self.start_y), (self.x, self.y)):
            intersected.append(room)
    return intersected if intersected else [self.target_room]

  def draw(self, surface: pygame.Surface) -> None:
    if self.subtype == "BIO" or self.w_type == "BIO_BEAM":
      if self.w_type == "BEAM":
        pygame.draw.line(surface, (50, 255, 100), (int(self.start_x), int(self.start_y)), (int(self.x), int(self.y)), 4)
        pygame.draw.circle(surface, (150, 255, 180), (int(self.x), int(self.y)), 7)
      else:
        pygame.draw.circle(surface, (50, 255, 120), (int(self.x), int(self.y)), 7)
        pygame.draw.circle(surface, (200, 255, 220), (int(self.x), int(self.y)), 3)
    elif self.subtype == "FIRE":
      if self.w_type == "BEAM":
        pygame.draw.line(surface, (255, 120, 0), (int(self.start_x), int(self.start_y)), (int(self.x), int(self.y)), 4)
        pygame.draw.circle(surface, (255, 220, 50), (int(self.x), int(self.y)), 8)
      else:
        pygame.draw.circle(surface, (255, 100, 0), (int(self.x), int(self.y)), 7)
        pygame.draw.circle(surface, (255, 220, 0), (int(self.x), int(self.y)), 4)
    elif self.subtype == "STUN":
      pygame.draw.circle(surface, (80, 220, 255), (int(self.x), int(self.y)), 8)
      pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 4)
    elif self.subtype == "BREACH":
      pygame.draw.circle(surface, (220, 40, 40), (int(self.x), int(self.y)), 8)
      pygame.draw.circle(surface, (100, 0, 0), (int(self.x), int(self.y)), 4)
    elif self.w_type == "MISSILE":
      pygame.draw.rect(
          surface, (255, 140, 0), (int(self.x) - 4, int(self.y) - 4, 8, 8)
      )
    elif self.w_type == "FLAK":
      pygame.draw.circle(surface, (255, 180, 50), (int(self.x) - 3, int(self.y) - 3), 4)
      pygame.draw.circle(surface, (255, 220, 100), (int(self.x) + 3, int(self.y) + 3), 4)
    elif self.w_type == "ION":
      pygame.draw.circle(surface, (50, 220, 255), (int(self.x), int(self.y)), 7)
      pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 4)
    elif self.w_type == "HEAVY_LASER" or self.subtype == "HEAVY":
      pygame.draw.circle(surface, (255, 50, 50), (int(self.x), int(self.y)), 9)
      pygame.draw.circle(surface, (255, 200, 200), (int(self.x), int(self.y)), 4)
    elif self.w_type == "BEAM":
      pygame.draw.line(
          surface, (255, 255, 100), (int(self.start_x), int(self.start_y)), (int(self.x), int(self.y)), 4
      )
      pygame.draw.circle(
          surface, (255, 255, 150), (int(self.x), int(self.y)), 7
      )
    else:  # LASER
      pygame.draw.circle(
          surface, COLOR_PROJECTILE, (int(self.x), int(self.y)), 5
      )
