import pygame
from classes.Room import Room


class Door:

    def __init__(self, room_a: Room, room_b: Room, rect: tuple[int, int, int, int]) -> None:
        self.room_a: Room = room_a
        self.room_b: Room = room_b
        self.rect: pygame.Rect = pygame.Rect(rect)
        self.is_open: bool = False

    def toggle(self) -> None:
        self.is_open = not self.is_open

    def update(self, dt: float) -> None:
        if self.is_open:
            avg_o2 = (self.room_a.oxygen + self.room_b.oxygen) / 2.0
            self.room_a.oxygen += (avg_o2 - self.room_a.oxygen) * 2.0 * dt
            self.room_b.oxygen += (avg_o2 - self.room_b.oxygen) * 2.0 * dt

    def draw(self, surface: pygame.Surface) -> None:
        color = (100, 255, 100) if self.is_open else (200, 50, 50)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 1)
