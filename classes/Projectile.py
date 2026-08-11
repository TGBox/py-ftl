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
      max_range: float | None = None,
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
    self.max_range: float | None = max_range
    self.distance_traveled: float = 0.0
    self.out_of_range: bool = False
    self.alive: bool = True

    dx = self.target_x - self.x
    dy = self.target_y - self.y
    dist = math.hypot(dx, dy)
    speed = 650.0 if w_type in ("BEAM", "BIO_BEAM") else (550.0 if w_type == "FLAK" else 400.0)
    self.vx: float = (dx / dist) * speed if dist != 0 else 0.0
    self.vy: float = (dy / dist) * speed if dist != 0 else 0.0
    
  def to_str(self) -> str:
    """Methode um eine String Repräsentation dieses Projectile Objekts zu generieren.

    Returns:
        str: Die String Repräsentation des Projectile Objekts.
    """
    p_str = (f"{"Spieler" if self.is_player_shot else "Gegnerisches"} Projektil von {self.w_type} "
             f"- {self.subtype} | Start: x={self.start_x}, y={self.start_y} | Ziel: {self.target_room.name} "
             f"bei x={self.target_x}, y={self.target_y} | Position: x={self.x}, y={self.y} | "
             f"Bisherige Flugdistanz: {self.distance_traveled} | Schaden: {self.damage} | "
             f"Schilddurchstoß: {self.shield_pierce} | Feuerchance: {self.fire_chance} % | "
             f"Hüllenbruchchance: {self.breach_chance} % | Betäubungsdauer: {self.stun_duration} | "
             f"Crewschaden: {self.crew_damage} | Maximale Reichweite: {self.max_range} | "
             f"Ausser Reichweite: {self.out_of_range} | Aktiv: {self.alive}")
    return p_str
  # TODO: Hier vielleicht noch die abhängigen Variablen der Klasse mit ausgeben? (dx, dy, speed, dist, ...)

  def update(self, dt: float) -> None:
    step_x = self.vx * dt
    step_y = self.vy * dt
    self.x += step_x
    self.y += step_y
    self.distance_traveled += math.hypot(step_x, step_y)

    if self.max_range is not None and self.distance_traveled >= self.max_range:
      self.alive = False
      self.out_of_range = True
      return

    if math.hypot(self.target_x - self.x, self.target_y - self.y) < 10:
      self.alive = False

  def get_intersected_rooms(self, rooms: list[Room]) -> list[Room]:
    """Prüft per Liniensegment-Schnittpunkt, welche Räume vom Beam gekreuzt werden (SRS Kap. 6.2)."""
    intersected: list[Room] = []
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

