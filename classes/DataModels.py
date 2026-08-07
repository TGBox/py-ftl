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
    subtype: str = "STANDARD"
    fire_chance: float = 0.0
    breach_chance: float = 0.0
    stun_duration: float = 0.0
    crew_damage: float = 0.0


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


class NodeSaveSchema(BaseModel):
    id: int
    x: int
    y: int
    event_type: str
    visited: bool = False
    connection_ids: list[int] = Field(default_factory=list)


class CrewSaveSchema(BaseModel):
    name: str
    species: str
    hp: float
    max_hp: float
    trait: str
    x: float
    y: float
    skill_repair: int = 0
    skill_combat: int = 0
    skill_piloting: int = 0
    skill_fitness: int = 0


class RoomSaveSchema(BaseModel):
    name: str
    health: float
    max_health: float
    current_power: int
    max_power: int
    oxygen: float
    has_breach: bool = False
    was_destroyed: bool = False


class WeaponSaveSchema(BaseModel):
    name: str
    charge_time: float
    w_type: str = "LASER"
    shield_pierce: int = 0
    damage: float = 35.0
    ammo_cost: int = 0
    level: int = 1
    subtype: str = "STANDARD"
    fire_chance: float = 0.0
    breach_chance: float = 0.0
    stun_duration: float = 0.0
    crew_damage: float = 0.0
    max_range: float | None = None


class SavegameSchema(BaseModel):
    schema_version: int = 2
    current_sector: int = 1
    rebel_fleet_x: float = 30.0
    sector_type: str = "Zivil"
    current_state: str = "MAP"
    current_node_id: int = 0
    nodes: list[NodeSaveSchema] = Field(default_factory=list)

    player_scrap: int = 20
    player_fuel: int = 6
    player_missiles: int = 6
    player_drone_parts: int = 5
    ship_name: str = "Kestrel"
    ship_hp: int = 15
    max_hp: int = 15
    reactor_total_power: int = 6
    reactor_available_power: int = 6
    shield_max_layers: int = 0

    rooms: list[RoomSaveSchema] = Field(default_factory=list)
    weapons: list[WeaponSaveSchema] = Field(default_factory=list)
    crew: list[CrewSaveSchema] = Field(default_factory=list)
    unlocked_ships: list[str] = Field(default_factory=lambda: ["Kestrel"])
