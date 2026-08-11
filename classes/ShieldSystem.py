import pygame

class ShieldSystem:

  def __init__(self, recharge_time: float = 4.0, hit_delay: float = 1.5) -> None:
    self.max_layers: int = 0
    self.current_layers: int = 0
    self.recharge_timer: float = 0.0
    self.recharge_time: float = recharge_time
    self.hit_delay: float = hit_delay
    self.lock_timer: float = 0.0
    
  def __str__(self) -> str:
    """Methode um einen von Menschen gut lesbaren String zu generieren, der dieses Schild Objekt repräsentiert.

    Returns:
        str: Der Repräsentationsstring.
    """
    s_str = f"SchildSystem mit {self.current_layers} / {self.max_layers}, Aufladetimer: {self.recharge_timer}, Aufladezeit: {self.recharge_time}, Trefferverzögerung: {self.hit_delay}, Blocktimer: {self.lock_timer}"
    return s_str

  def update(self, dt: float, powered_layers: int) -> None:
    self.max_layers = powered_layers
    if self.lock_timer > 0.0:
      self.lock_timer = max(0.0, self.lock_timer - dt)
      return

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
      # Trefferverzögerung vor Erholungsbeginn
      self.recharge_timer = -self.hit_delay
      return True
    return False

  def draw_bubble(
      self, surface: pygame.Surface, center: tuple[int, int], base_radius: int
  ) -> None:
    for i in range(self.current_layers):
      radius = base_radius + (i * 12)
      pygame.draw.circle(surface, (80, 150, 255), center, radius, 3)