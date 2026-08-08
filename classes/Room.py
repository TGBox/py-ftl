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
    self.fire_level: float = 0.0  # Feuer (0.0 bis 100.0)
    self.ion_timer: float = 0.0  # Ion-Sperre (Sekunden)
    self.was_destroyed: bool = False  # Komplett zerstört (0 HP)

  def effective_max_power(self) -> int:
    eff = math.floor(self.max_power * (self.health / self.max_health))
    if self.ion_timer > 0.0:
        eff = max(0, eff - 1)
    return max(0, eff)

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
    if self.health <= 0.0:
        self.was_destroyed = True
    import random
    if random.random() < 0.35:
        self.has_breach = True
    if random.random() < 0.30:
        self.fire_level = min(100.0, self.fire_level + 35.0)
    while self.current_power > self.effective_max_power():
      self.remove_power(reactor)

  def repair(self, amount: float) -> None:
    if self.health <= 0.0:
        self.was_destroyed = True

    if self.has_breach:
        self.has_breach = False
        return
    if self.fire_level > 0.0:
        self.fire_level = max(0.0, self.fire_level - amount * 1.5)
        return

    # Komplett zerstörte Gegner-Räume benötigen 5-mal so lange zum Reparieren
    effective_amount = amount
    if self.is_enemy and getattr(self, "was_destroyed", False):
        effective_amount = amount / 5.0

    self.health = min(self.max_health, self.health + effective_amount)
    if self.health >= self.max_health:
        self.was_destroyed = False

  def update_oxygen(self, dt: float, connected_rooms: list["Room"] = None) -> None:
    """Updates oxygen levels, fire processing, and ion timers for FTL room simulation."""
    self.ion_timer = max(0.0, self.ion_timer - dt)

    if self.has_breach:
      self.oxygen = max(0.0, self.oxygen - 25.0 * dt)
    elif self.health < 40.0:
      self.oxygen = max(0.0, self.oxygen - 8.0 * dt)
    elif self.current_power > 0 or not self.is_enemy:
      self.oxygen = min(100.0, self.oxygen + 3.0 * dt)

    # Feuer-Verarbeitung & Vakuum-Löschung
    if self.fire_level > 0.0:
      if self.oxygen < 10.0:
        # Vakuum erstickt das Feuer!
        self.fire_level = max(0.0, self.fire_level - 40.0 * dt)
      else:
        self.oxygen = max(0.0, self.oxygen - (15.0 * self.fire_level / 100.0) * dt)
        self.health = max(0.0, self.health - (6.0 * self.fire_level / 100.0) * dt)

        # Feuer-Ausbreitung bei hoher Intensität
        if self.fire_level > 60.0 and self.oxygen > 20.0 and connected_rooms:
          import random
          if random.random() < 0.15 * dt:
            target = random.choice(connected_rooms)
            target.fire_level = min(100.0, target.fire_level + 20.0)

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

    # Medbay spezielles Styling
    if self.name == "Medbay":
        border_col = (80, 220, 120) if self.current_power > 0 else (60, 100, 70)
        fill_col = (20, 45, 30) if self.current_power > 0 else (15, 25, 20)

    pygame.draw.rect(surface, fill_col, self.rect)
    pygame.draw.rect(surface, border_col, self.rect, 2)

    # Ion-Sperren Animation & Overlay
    if self.ion_timer > 0.0:
        import random
        cx, cy = self.rect.centerx, self.rect.centery
        for _ in range(3):
            ix = cx + random.randint(-self.rect.width // 4, self.rect.width // 4)
            iy = cy + random.randint(-self.rect.height // 4, self.rect.height // 4)
            pygame.draw.circle(surface, (100, 220, 255), (ix, iy), random.randint(3, 6))
        ion_lbl = get_font(13, bold=True).render(f"ION ({int(self.ion_timer)}s)", True, (100, 220, 255))
        surface.blit(ion_lbl, (self.rect.x + 6, self.rect.y + 36))

    # Feuer-Animation & Overlay
    if self.fire_level > 0.0:
        import random
        # Flammen-Partikel zeichnen
        cx, cy = self.rect.centerx, self.rect.centery
        for _ in range(int(min(8, 2 + self.fire_level / 15))):
            fx = cx + random.randint(-self.rect.width // 4, self.rect.width // 4)
            fy = cy + random.randint(-self.rect.height // 4, self.rect.height // 4)
            fr = random.randint(4, 10)
            f_col = random.choice([(255, 60, 0), (255, 140, 0), (255, 220, 0)])
            pygame.draw.circle(surface, f_col, (fx, fy), fr)

        fire_lbl = get_font(14, bold=True).render("FEUER", True, (255, 100, 0))
        surface.blit(fire_lbl, (self.rect.x + 6, self.rect.bottom - 16))

    # Zerstört 5x Reparatur Overlay für Gegner-Räume
    if self.is_enemy and getattr(self, "was_destroyed", False) and self.health < self.max_health:
        dest_lbl = get_font(12, bold=True).render("ZERSTÖRT (5X REP)", True, (255, 60, 60))
        surface.blit(dest_lbl, (self.rect.x + 6, self.rect.y + 36))

    surface.blit(
        get_font(14, bold=True).render(self.name, True, (230, 240, 255)),
        (self.rect.x + 6, self.rect.y + 4),
    )

    if self.name == "Medbay" and self.current_power > 0:
        heal_lbl = get_font(13, bold=True).render("+HEILEN", True, (100, 255, 100))
        surface.blit(heal_lbl, (self.rect.x + 6, self.rect.y + 28))

    # System-Gesundheitsbalken
    hp_ratio = self.health / self.max_health
    hp_color = COLOR_HP_GREEN if hp_ratio > 0.4 else COLOR_HP_RED
    pygame.draw.rect(
        surface,
        (30, 30, 30),
        (self.rect.x + 6, self.rect.y + 20, self.rect.width - 12, 3),
    )
    pygame.draw.rect(
        surface,
        hp_color,
        (
            self.rect.x + 6,
            self.rect.y + 20,
            int((self.rect.width - 12) * hp_ratio),
            3,
        ),
    )

    # Sauerstoffanzeige (O2: 100%)
    o2_color = (100, 220, 255) if self.oxygen > 40.0 else (255, 100, 100)
    o2_txt = get_font(12, bold=True).render(f"O2:{int(self.oxygen)}%", True, o2_color)
    surface.blit(o2_txt, (self.rect.right - 36, self.rect.y + 5))

    # Hüllenleck Icon zeichnen (falls vorhanden)
    if self.has_breach:
        cx, cy = self.rect.centerx, self.rect.centery
        pygame.draw.circle(surface, (15, 15, 15), (cx, cy), 12)
        pygame.draw.circle(surface, (255, 50, 50), (cx, cy), 13, 2)
        lbl = get_font(14, bold=True).render("LECK", True, (255, 80, 80))
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

