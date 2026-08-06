import math
import pygame

from classes.Room import Room
from settings import COLOR_CREW, COLOR_SELECTED


import random

SPECIES_NAMES = {
    "Mensch": ["Vance", "Sarah", "Jackson", "Elena", "Marcus", "David", "Lisa", "Alex"],
    "Engi": ["Slockat", "Tuco", "Kaz", "01-Beta", "Xix", "N-402", "Kael"],
    "Mantis": ["Kazaak", "Ruwen", "Skraak", "Zazz", "Kazaakth", "Voraak"],
}

CREW_TRAITS = ["Sprinter", "Sauerstoff-Sparer", "Feuerwehr", "Kampfveteran"]


class Crew:

    def __init__(
        self,
        x: float,
        y: float,
        name: str = "",
        species: str = "Mensch",
        is_enemy: bool = False,
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.radius: int = 12
        self.selected: bool = False
        self.target_pos: tuple[int, int] | None = None
        self.species: str = species
        self.name: str = name if name else random.choice(SPECIES_NAMES.get(species, ["Crew"]))
        self.is_enemy: bool = is_enemy
        self.hp: float = 100.0
        self.max_hp: float = 100.0
        self.current_room: Room | None = None
        self.trait: str = random.choice(CREW_TRAITS)

        self.is_boarding: bool = False
        self.stun_timer: float = 0.0

        # Spezies-Eigenschaften (Reparatur & Nahkampf)
        if self.species == "Engi":
            self.repair_multiplier: float = 2.0
            self.melee_multiplier: float = 0.5
        elif self.species == "Mantis":
            self.repair_multiplier: float = 0.6
            self.melee_multiplier: float = 2.0
        else:  # Mensch / standard
            self.repair_multiplier: float = 1.0
            self.melee_multiplier: float = 1.0

        if self.trait == "Feuerwehr":
            self.repair_multiplier *= 1.4
        elif self.trait == "Kampfveteran":
            self.melee_multiplier += 0.3

        self.move_speed: float = 160.0 if self.trait == "Sprinter" else 120.0

    def update(self, dt: float, rooms: list[Room]) -> None:
        if self.stun_timer > 0.0:
            self.stun_timer = max(0.0, self.stun_timer - dt)
            # Gelähmt: Kann sich weder bewegen noch reparieren
            self.current_room = None
            for room in rooms:
                if room.rect.collidepoint(int(self.x), int(self.y)):
                    self.current_room = room
                    break
            return

        if self.target_pos:
            tx, ty = self.target_pos
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            if dist < self.move_speed * dt:
                self.x, self.y = float(tx), float(ty)
                self.target_pos = None
            else:
                self.x += (dx / dist) * self.move_speed * dt
                self.y += (dy / dist) * self.move_speed * dt

        self.current_room = None
        for room in rooms:
            if room.rect.collidepoint(int(self.x), int(self.y)):
                self.current_room = room
                if not self.target_pos and room.health < room.max_health:
                    room.repair(25.0 * self.repair_multiplier * dt)
                break

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_enemy:
            base_color = (255, 80, 80)
        elif self.species == "Engi":
            base_color = (100, 200, 255)
        elif self.species == "Mantis":
            base_color = (200, 255, 100)
        else:
            base_color = COLOR_CREW

        color = COLOR_SELECTED if self.selected else base_color

        pygame.draw.circle(
            surface, color, (int(self.x), int(self.y)), self.radius
        )
        pygame.draw.circle(
            surface, (255, 255, 255) if self.selected else (0, 0, 0), (int(self.x), int(self.y)), self.radius, 1
        )

        # Stun-Effekt Overlay (Funken um Crew-Mitglied)
        if self.stun_timer > 0.0:
            for _ in range(3):
                sx = int(self.x) + random.randint(-14, 14)
                sy = int(self.y) + random.randint(-14, 14)
                s_color = random.choice([(100, 240, 255), (255, 255, 100), (200, 220, 255)])
                pygame.draw.circle(surface, s_color, (sx, sy), random.randint(2, 4))
            b_font = pygame.font.SysFont(None, 12, bold=True)
            stun_lbl = b_font.render("STUN", True, (100, 240, 255))
            surface.blit(stun_lbl, (int(self.x) - stun_lbl.get_width() // 2, int(self.y) - self.radius - 16))

        # HP-Balken über dem Crewmitglied
        if self.hp < self.max_hp or self.selected:
            bar_w = 20
            bar_h = 3
            bar_x = int(self.x) - bar_w // 2
            bar_y = int(self.y) - self.radius - 6
            hp_ratio = max(0.0, self.hp / self.max_hp)
            pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surface, (50, 220, 100), (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

        # Spezies-Badge Buchstabe im Kreis
        badge_font = pygame.font.SysFont(None, 14, bold=True)
        badge_char = "P" if self.is_enemy else (self.species[0] if self.species else "C")
        badge_lbl = badge_font.render(badge_char, True, (0, 0, 0) if self.selected else (255, 255, 255))
        surface.blit(badge_lbl, (int(self.x) - badge_lbl.get_width() // 2, int(self.y) - badge_lbl.get_height() // 2))

        # Name & Trait-Badge zeichnen
        font = pygame.font.SysFont(None, 13)
        trait_str = f" [{self.trait[:4]}]" if hasattr(self, "trait") and self.trait else ""
        lbl = font.render(f"{self.name}{trait_str}", True, (220, 240, 255))
        surface.blit(lbl, (int(self.x) - lbl.get_width() // 2, int(self.y) + self.radius + 2))

