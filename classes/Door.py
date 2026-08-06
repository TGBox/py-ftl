import pygame
from classes.Room import Room


class Door:

    def __init__(
        self,
        room_a: Room,
        room_b: Room | None,
        rect: tuple[int, int, int, int],
        is_airlock: bool = False,
    ) -> None:
        self.room_a: Room = room_a
        self.room_b: Room | None = room_b
        self.rect: pygame.Rect = pygame.Rect(rect)
        self.is_open: bool = False
        self.is_airlock: bool = is_airlock

    def toggle(self) -> None:
        self.is_open = not self.is_open

    def update(self, dt: float) -> None:
        if not self.is_open:
            return

        if self.is_airlock or self.room_b is None:
            # Druckausgleich mit Weltall (Sauerstoff entweicht ins Vakuum!)
            if self.room_a:
                self.room_a.oxygen = max(0.0, self.room_a.oxygen - 45.0 * dt)
        else:
            # Druckausgleich zwischen zwei Räumen
            avg_o2 = (self.room_a.oxygen + self.room_b.oxygen) / 2.0
            self.room_a.oxygen += (avg_o2 - self.room_a.oxygen) * 3.0 * dt
            self.room_b.oxygen += (avg_o2 - self.room_b.oxygen) * 3.0 * dt

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_airlock:
            color = (0, 220, 255) if self.is_open else (220, 100, 40)
            border_col = (150, 240, 255) if self.is_open else (255, 180, 100)
        else:
            color = (100, 255, 100) if self.is_open else (200, 50, 50)
            border_col = (255, 255, 255)

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, border_col, self.rect, 1)
