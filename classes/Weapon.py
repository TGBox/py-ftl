class Weapon:

  def __init__(
      self,
      name: str,
      charge_time: float,
      w_type: str = "LASER",
      ammo_cost: int = 0,
      shield_pierce: int = 0,
      damage: float = 35.0,
  ) -> None:
    self.name: str = name
    self.charge_time: float = charge_time
    self.current_charge: float = 0.0
    self.w_type: str = w_type  # "LASER", "MISSILE", "BEAM"
    self.ammo_cost: int = ammo_cost
    self.shield_pierce: int = shield_pierce
    self.damage: float = damage
    self.level: int = 1  # Upgradestufe (1 bis 3)

  def upgrade(self) -> bool:
    if self.level < 3:
      self.level += 1
      self.damage = round(self.damage * 1.25, 1)
      self.charge_time = max(1.5, round(self.charge_time * 0.85, 1))
      self.name = f"{self.name.split(' (L')[0]} (Lvl {self.level})"
      return True
    return False

  def update(self, dt: float, powered: bool) -> None:
    if powered:
      self.current_charge = min(self.charge_time, self.current_charge + dt)

  def is_ready(self) -> bool:
    return self.current_charge >= self.charge_time

  def reset(self) -> None:
    self.current_charge = 0.0