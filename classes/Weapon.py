from enums import WeaponType, WeaponSubtype


class Weapon:

  def __init__(
      self,
      name: str,
      charge_time: float,
      w_type: WeaponType | str = WeaponType.LASER,
      ammo_cost: int = 0,
      shield_pierce: int = 0,
      damage: float = 35.0,
      level: int = 1,
      subtype: WeaponSubtype | str = WeaponSubtype.STANDARD,
      fire_chance: float = 0.0,
      breach_chance: float = 0.0,
      stun_duration: float = 0.0,
      crew_damage: float = 0.0,
      max_range: float | None = None,
  ) -> None:
    self.name: str = name
    self.charge_time: float = charge_time
    self.current_charge: float = 0.0
    self.w_type: WeaponType | str = w_type  # "LASER", "MISSILE", "BEAM", "ION", "BOMB", "FLAK"
    self.ammo_cost: int = ammo_cost
    self.shield_pierce: int = shield_pierce
    self.damage: float = damage
    self.level: int = level  # Upgradestufe (1 bis 5)
    self.subtype: WeaponSubtype | str = subtype  # "STANDARD", "BIO", "FIRE", "BREACH", "STUN", "HEAVY"
    self.fire_chance: float = fire_chance
    self.breach_chance: float = breach_chance
    self.stun_duration: float = stun_duration
    self.crew_damage: float = crew_damage
    self.max_range: float | None = max_range

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

  def __str__(self) -> str:
    """Methode um eine String Repräsentation dieses Waffenobjekts zu erstellen, die von Menschen gut gelesen werden kann.

    Returns:
        str: Die String Repräsentation des Objekts.
    """
    w_str = f"Level {self.level} Waffe - \"{self.name}\" vom Typ {self.w_type} mit Subtyp {self.subtype}. Ladezeit: {self.charge_time}, Aktuelle Ladung: {self.current_charge}, Munitionskosten: {self.ammo_cost}\n"
    w_str += f"Schaden: {self.damage}, Crew-Schaden: {self.crew_damage}, Schilddurchdringung: {self.shield_pierce}\n"
    w_str += f"Feuerchance: {self.fire_chance}, Hüllenbruchchance: {self.breach_chance}, Betäubungsdauer: {self.stun_duration}, Reichweite: {self.max_range}"
    return w_str