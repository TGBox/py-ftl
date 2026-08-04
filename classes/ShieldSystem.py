import pygame

class ShieldSystem:
  def __init__(self, recharge_time: float = 4.0) -> None:
    self.max_layers: int = 0
    self.current_layers: int = 0
    self.recharge_timer: float = 0.0
    self.recharge_time: float = recharge_time

  def update(self, dt: float, powered_layers: int) -> None:
    self.max_layers = powered_layers
    if self.current_layers > self.max_layers:
      self.current_layers = self.max_layers

    if self.current_layers < self.max_layers:
      self.recharge_timer += dt
      if self.recharge_timer >= self.recharge_time:
        self.current_layers += 1
        self.recharge_timer = 0.0
    else:
      self.recharge_timer = 0.0

  def attempt_block(self) -> bool:
    if self.current_layers > 0:
      self.current_layers -= 1
      self.recharge_timer = 0.0
      return True
    return False

  # NEU: Zeichnet die Schildblasen um das Schiff
  def draw_bubble(self, surface: pygame.Surface, center: tuple[int, int], base_radius: int) -> None:
    for i in range(self.current_layers):
      # Jede weitere Schildschicht wird etwas größer gezeichnet
      radius = base_radius + (i * 12)
      pygame.draw.circle(surface, (80, 150, 255), center, radius, 3)