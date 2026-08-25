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
        self.opened_by_crew: bool = False

    def toggle(self) -> None:
        self.is_open = not self.is_open
        self.opened_by_crew = False

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

    def draw(self, surface: pygame.Surface, door_level: int = 1) -> None:
        if self.is_airlock:
            color = (0, 220, 255) if self.is_open else (220, 100, 40)
            border_col = (150, 240, 255) if self.is_open else (255, 180, 100)
        else:
            if self.is_open:
                color = (100, 255, 100)
                border_col = (255, 255, 255)
            else:
                color = (220, 160, 40) if door_level >= 3 else ((180, 140, 60) if door_level == 2 else (200, 50, 50))
                border_col = (255, 220, 100) if door_level >= 3 else ((200, 200, 220) if door_level == 2 else (255, 255, 255))

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, border_col, self.rect, 1 if door_level <= 1 else 2)

        # Gepanzerter Schottestüren Schloss-Indikator
        if not self.is_open and door_level >= 3:
            pygame.draw.circle(surface, (255, 220, 80), self.rect.center, 3)

    def __str__(self) -> str:
        """Methode um eine von Menschen gut lesbare String Repräsentation dieses Tür Objektes zu generieren.

        Returns:
            str: Die String Repräsentation dieses Objekts.
        """
        if self.room_b is None:
            d_str = f"Tür zwischen Raum {self.room_a.name} und der Aussenseite des Schiffs, "
        else:
            d_str = f"Tür zwischen Raum {self.room_a.name} und Raum {self.room_b.name}, "
        d_str += f"mit Position x={self.rect.x}, y={self.rect.y}, Status: {"Geöffnet" if self.is_open else "Geschlossen"}, Ist Luftschleuse: {self.is_airlock}, wurde durch Crew geöffnet: {self.opened_by_crew}."
        return d_str