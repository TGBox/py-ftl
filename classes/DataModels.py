from typing import Any
from pydantic import BaseModel, Field


class WeaponSchema(BaseModel):
    name: str
    charge_time: float
    w_type: str = "LASER"
    shield_pierce: int = 0
    damage: float = 35.0
    ammo_cost: int = 0
    level: int = 1



class RoomConfigSchema(BaseModel):
    type: str
    pos: tuple[int, int]
    size: tuple[int, int]
    max_power: int = 1


class ShipBlueprintSchema(BaseModel):
    name: str
    max_hp: int
    max_weapons: int = 3
    max_crew: int = 4
    rooms_config: list[RoomConfigSchema]


class EventChoiceSchema(BaseModel):
    text: str
    action: str
    requires: str | None = None  # e.g., "crew_Engi" or "system_shield_level_2" (SRS Kap. 7.2)
    is_blue: bool = False
    scrap: int = 0
    fuel: int = 0


class EventNodeSchema(BaseModel):
    event_id: str
    event_type: str
    text: str
    choices: list[EventChoiceSchema]


class SavegameSchema(BaseModel):
    schema_version: int = 1
    current_sector: int = 1
    player_scrap: int = 10
    player_fuel: int = 10
    player_missiles: int = 5
    ship_name: str = "Kestrel"
    ship_hp: int = 15
