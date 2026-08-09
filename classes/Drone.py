import math
import random


class Drone:
    """Represents an active or cataloged drone with specialized AI, power, and role."""

    def __init__(
        self,
        name: str,
        drone_type: str,
        power_cost: int,
        desc: str,
        hotkey: str,
        hp: float = 100.0,
    ):
        self.name = name
        self.drone_type = drone_type  # COMBAT_MK1, REPAIR, DEFENSE_MK1, SHIELD_CHARGER, ANTI_PERSONNEL
        self.power_cost = power_cost
        self.desc = desc
        self.hotkey = hotkey
        self.active = False
        self.hp = hp
        self.max_hp = hp
        self.x = 0.0
        self.y = 0.0
        self.target_pos: tuple[float, float] | None = None
        self.cooldown = 0.0
        self.orbit_angle = random.uniform(0, 2 * math.pi)

    def reset(self):
        self.active = False
        self.hp = self.max_hp
        self.cooldown = 0.0
        self.target_pos = None


# Master list of all available drone blueprints
DRONE_CATALOG: list[Drone] = [
    Drone("Kampfdrohne MK I", "COMBAT_MK1", 1, "Umkreist den Gegner und schießt Lasersalven.", "K"),
    Drone("Reparatur-Drohne", "REPAIR", 1, "Repariert beschädigte Räume (+25 HP/s) & Brüchte.", "D"),
    Drone("Verteidigungs-Drohne MK I", "DEFENSE_MK1", 2, "Schießt feindliche Raketen & Asteroiden ab.", "F"),
    Drone("Schild-Lade-Drohne", "SHIELD_CHARGER", 2, "Erhöht Schild-Laderate & gewährt Overshield.", "E"),
    Drone("Anti-Personen-Drohne", "ANTI_PERSONNEL", 2, "Bekämpft feindliche Entermannschaften (150 HP).", "P"),
]
