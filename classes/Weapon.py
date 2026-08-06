class Weapon:

  def __init__(
      self,
      name: str,
      charge_time: float,
      w_type: str = "LASER",
      ammo_cost: int = 0,
      shield_pierce: int = 0,
      damage: float = 35.0,
      level: int = 1,
      subtype: str = "STANDARD",
      fire_chance: float = 0.0,
      breach_chance: float = 0.0,
      stun_duration: float = 0.0,
      crew_damage: float = 0.0,
  ) -> None:
    self.name: str = name
    self.charge_time: float = charge_time
    self.current_charge: float = 0.0
    self.w_type: str = w_type  # "LASER", "MISSILE", "BEAM", "ION", "BOMB", "FLAK"
    self.ammo_cost: int = ammo_cost
    self.shield_pierce: int = shield_pierce
    self.damage: float = damage
    self.level: int = level  # Upgradestufe (1 bis 5)
    self.subtype: str = subtype  # "STANDARD", "BIO", "FIRE", "BREACH", "STUN", "HEAVY"
    self.fire_chance: float = fire_chance
    self.breach_chance: float = breach_chance
    self.stun_duration: float = stun_duration
    self.crew_damage: float = crew_damage

  def upgrade(self) -> bool:
    if self.level < 5:
      self.level += 1
      self.damage = round(self.damage * 1.25, 1)
      if self.crew_damage > 0:
        self.crew_damage = round(self.crew_damage * 1.2, 1)
      self.charge_time = max(1.2, round(self.charge_time * 0.85, 1))
      roman = ["I", "II", "III", "IV", "V"]
      base_name = self.name.split(" MK")[0].split(" (Lvl")[0]
      self.name = f"{base_name} MK {roman[self.level - 1]}"
      return True
    return False

  def update(self, dt: float, powered: bool) -> None:
    if powered:
      self.current_charge = min(self.charge_time, self.current_charge + dt)

  def is_ready(self) -> bool:
    return self.current_charge >= self.charge_time

  def reset(self) -> None:
    self.current_charge = 0.0