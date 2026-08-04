class Weapon:

  def __init__(self, name: str = "Laser", charge_time: float = 3.0) -> None:
    self.name: str = name
    self.charge_time: float = charge_time
    self.current_charge: float = 0.0
    self.auto_fire: bool = False

  def update(self, dt: float, powered: bool) -> None:
    if powered:
      self.current_charge = min(self.charge_time, self.current_charge + dt)

  def is_ready(self) -> bool:
    return self.current_charge >= self.charge_time

  def reset(self) -> None:
    self.current_charge = 0.0