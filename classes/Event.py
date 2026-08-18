from dataclasses import dataclass, field
from typing import Any, Optional, Union


@dataclass
class EventChoice:
    text: str = ""
    label: str = ""
    action: str = "CONTINUE"
    is_blue: bool = False
    requires_species: Optional[str] = None
    scrap: int = 0
    fuel: int = 0
    missiles: int = 0
    drones: int = 0
    damage: int = 0
    result_text: str = ""
    outcomes: Optional[list[dict[str, Any]]] = None
    requires_scrap: int = 0
    requires_fuel: int = 0
    requires_missiles: int = 0
    requires_drones: int = 0
    raw_data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.label and self.text:
            self.label = self.text
        elif not self.text and self.label:
            self.text = self.label

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None:
                return val
        return self.raw_data.get(key)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None and val != "":
                return val
            if key in ("text", "label") and val == "":
                return self.label if key == "text" else self.text
        return self.raw_data.get(key, default)

    def __contains__(self, key: str) -> bool:
        if hasattr(self, key) and getattr(self, key) is not None:
            return True
        return key in self.raw_data

    @classmethod
    def from_dict(cls, data: Union[dict[str, Any], "EventChoice"]) -> "EventChoice":
        if isinstance(data, EventChoice):
            return data
        d = dict(data)
        text = d.get("text", d.get("label", ""))
        label = d.get("label", d.get("text", ""))
        action = str(d.get("action", "CONTINUE"))
        is_blue = bool(d.get("is_blue", False))
        requires_species = d.get("requires_species")
        scrap = int(d.get("scrap", 0))
        fuel = int(d.get("fuel", 0))
        missiles = int(d.get("missiles", 0))
        drones = int(d.get("drones", d.get("drone_parts", 0)))
        damage = int(d.get("damage", 0))
        result_text = str(d.get("result_text", ""))
        outcomes = d.get("outcomes")
        req_scrap = int(d.get("requires_scrap", 0))
        req_fuel = int(d.get("requires_fuel", 0))
        req_missiles = int(d.get("requires_missiles", 0))
        req_drones = int(d.get("requires_drones", d.get("requires_drone_parts", 0)))
        return cls(
            text=text,
            label=label,
            action=action,
            is_blue=is_blue,
            requires_species=requires_species,
            scrap=scrap,
            fuel=fuel,
            missiles=missiles,
            drones=drones,
            damage=damage,
            result_text=result_text,
            outcomes=outcomes,
            requires_scrap=req_scrap,
            requires_fuel=req_fuel,
            requires_missiles=req_missiles,
            requires_drones=req_drones,
            raw_data=d,
        )

    def to_dict(self) -> dict[str, Any]:
        res = dict(self.raw_data)
        res.update({
            "text": self.text,
            "label": self.label,
            "action": self.action,
            "is_blue": self.is_blue,
            "requires_species": self.requires_species,
            "scrap": self.scrap,
            "fuel": self.fuel,
            "missiles": self.missiles,
            "drones": self.drones,
            "damage": self.damage,
            "result_text": self.result_text,
        })
        if self.outcomes is not None:
            res["outcomes"] = self.outcomes
        return res


@dataclass
class Event:
    event_type: str = ""
    text: str = ""
    choices: list[EventChoice] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None:
                return val
        return self.raw_data.get(key)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None:
                return val
        return self.raw_data.get(key, default)

    def __contains__(self, key: str) -> bool:
        if hasattr(self, key) and getattr(self, key) is not None:
            return True
        return key in self.raw_data

    @classmethod
    def from_dict(cls, data: Union[dict[str, Any], "Event"]) -> "Event":
        if isinstance(data, Event):
            return data
        d = dict(data)
        event_type = str(d.get("event_type", ""))
        text = str(d.get("text", ""))
        raw_choices = d.get("choices", [])
        choices = [EventChoice.from_dict(c) for c in raw_choices]
        return cls(
            event_type=event_type,
            text=text,
            choices=choices,
            raw_data=d,
        )

    def to_dict(self) -> dict[str, Any]:
        res = dict(self.raw_data)
        res.update({
            "event_type": self.event_type,
            "text": self.text,
            "choices": [c.to_dict() for c in self.choices],
        })
        return res
