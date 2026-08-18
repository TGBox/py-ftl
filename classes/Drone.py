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
        self.equipped = True
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
        
    def __str__(self) -> str:
        """Methode um eine von Menschen gut lesbare String Repräsentation dieses Drohnen Objekts zu generieren.

        Returns:
            str: Die String Repräsentation des Drohnen Objekts.
        """
        d_str = f"Drohne \"{self.name}\" vom Typ {self.drone_type}, Gesundheit: {self.hp} / {self.max_hp}, Stromkosten: {self.power_cost}, Desc: {self.desc}, Hotkey: {self.hotkey}, "
        d_str += f"Position: x={self.x}, y={self.y}, Zielposition: "
        if self.target_pos is None:
            d_str += "Keine, "
        else:
            d_str += f"x={self.target_pos[0]}, y={self.target_pos[1]}, "
        d_str += f"Cooldown: {self.cooldown}, Orbitwinkel: {self.orbit_angle}, Aktiv: {self.active}"
        return d_str


# Master list of all available drone blueprints
DRONE_CATALOG: list[Drone] = [
    Drone("Kampfdrohne MK I", "COMBAT_MK1", 1, "Umkreist den Gegner und schießt Lasersalven.", "K"),
    Drone("Reparatur-Drohne", "REPAIR", 1, "Repariert beschädigte Räume (+25 HP/s) & Brüchte.", "D"),
    Drone("Verteidigungs-Drohne MK I", "DEFENSE_MK1", 2, "Schießt feindliche Raketen & Asteroiden ab.", "F"),
    Drone("Schild-Lade-Drohne", "SHIELD_CHARGER", 2, "Erhöht Schild-Laderate & gewährt Overshield.", "E"),
    Drone("Anti-Personen-Drohne", "ANTI_PERSONNEL", 2, "Bekämpft feindliche Entermannschaften (150 HP).", "P"),
]
