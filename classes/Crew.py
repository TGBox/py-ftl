import math
import pygame

from classes.Room import Room
from settings import COLOR_CREW, COLOR_SELECTED


class Crew:

    def __init__(
        self,
        x: float,
        y: float,
        name: str = "Crew",
        species: str = "Mensch",
        is_enemy: bool = False,
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.radius: int = 12
        self.selected: bool = False
        self.target_pos: tuple[int, int] | None = None
        self.name: str = name
        self.species: str = species
        self.is_enemy: bool = is_enemy
        self.hp: float = 100.0
        self.max_hp: float = 100.0
        self.current_room: Room | None = None

        # Spezies-Eigenschaften
        if self.species == "Engi":
            self.repair_multiplier: float = 2.0
        elif self.species == "Mantis":
            self.repair_multiplier: float = 0.6
        else:  # Mensch / standard
            self.repair_multiplier: float = 1.0

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

        # HP-Balken über dem Crewmitglied
        if self.hp < self.max_hp or self.selected:
            bar_w = 20
            bar_h = 3
            bar_x = int(self.x) - bar_w // 2
            bar_y = int(self.y) - self.radius - 6
            hp_ratio = max(0.0, self.hp / self.max_hp)
            pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surface, (50, 220, 100), (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

        # Name zeichnen
        font = pygame.font.SysFont(None, 14)
        lbl = font.render(self.name, True, (220, 220, 220))
        surface.blit(lbl, (int(self.x) - lbl.get_width() // 2, int(self.y) + self.radius + 2))