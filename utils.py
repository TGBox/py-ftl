from typing import Any, Optional, Union
from classes.GameData import PlayerData
from classes.Room import Room
import pygame


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """Wraps text into lines that do not exceed max_width pixels when rendered by font."""
    if not text:
        return []
    lines: list[str] = []
    paragraphs = text.split("\n")
    for paragraph in paragraphs:
        words = paragraph.split(" ")
        current_line = ""
        for word in words:
            if not word:
                continue
            test_line = f"{current_line} {word}" if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        elif not paragraph:
            lines.append("")
    return lines


from classes.Event import EventChoice

def calculate_event_layout(
    ev_text: str,
    res_text: str,
    choices: list[Union[EventChoice, dict[str, Any]]],
    font: pygame.font.Font,
    box_x: int = 120,
    box_y: int = 100,
    box_width: int = 660,
    min_box_height: int = 380,
    max_text_width: int = 600,
) -> dict[str, Any]:
    """Calculates dynamic layout positions for event panel text, result text, and choice buttons."""
    ev_lines = wrap_text(ev_text, font, max_text_width)
    start_y = box_y + 25
    line_height = 24

    text_end_y = start_y + max(1, len(ev_lines)) * line_height

    res_lines = []
    if res_text:
        res_lines = wrap_text(res_text, font, max_text_width)
        res_start_y = text_end_y + 10
        res_end_y = res_start_y + len(res_lines) * line_height
        cont_btn_y = max(400, res_end_y + 15)
        last_y = cont_btn_y + 42 + 20
        box_height = max(min_box_height, last_y - box_y)
        return {
            "ev_lines": ev_lines,
            "res_lines": res_lines,
            "res_start_y": res_start_y,
            "cont_btn": pygame.Rect(box_x + 160, cont_btn_y, 340, 42),
            "choice_rects": [],
            "box_rect": pygame.Rect(box_x, box_y, box_width, box_height),
        }

    btn_start_y = max(200, text_end_y + 15)
    choice_rects: list[pygame.Rect] = []
    if not choices:
        cont_btn_y = max(400, btn_start_y)
        last_y = cont_btn_y + 42 + 20
        box_height = max(min_box_height, last_y - box_y)
        return {
            "ev_lines": ev_lines,
            "res_lines": [],
            "res_start_y": 0,
            "cont_btn": pygame.Rect(box_x + 160, cont_btn_y, 340, 42),
            "choice_rects": [],
            "box_rect": pygame.Rect(box_x, box_y, box_width, box_height),
        }

    for idx, _ in enumerate(choices):
        btn_y = btn_start_y + idx * 44
        choice_rects.append(pygame.Rect(box_x + 30, btn_y, 600, 38))

    last_y = (btn_start_y + len(choices) * 44) + 20
    box_height = max(min_box_height, last_y - box_y)

    return {
        "ev_lines": ev_lines,
        "res_lines": [],
        "res_start_y": 0,
        "cont_btn": None,
        "choice_rects": choice_rects,
        "box_rect": pygame.Rect(box_x, box_y, box_width, box_height),
    }


def get_room_manning_bonus(room_name: str, crew_count: int, room: Optional[Room] | None = None) -> dict[str, Any]:
    """Returns manning bonus multipliers and description based on room name, stationed crew count, and room power ratio."""
    power_ratio = 1.0
    if room is not None:
        max_p = max(1, getattr(room, "max_power", 1))
        curr_p = getattr(room, "current_power", 0)
        power_ratio = (curr_p / max_p) if curr_p > 0 else 0.0

    if crew_count <= 0:
        mult = 1.0 * power_ratio
        return {"multiplier": mult, "evasion": 0.0, "power_ratio": power_ratio, "desc": "Unbemannt" if power_ratio > 0 else "Kein Strom"}

    count = min(2, crew_count)

    if room_name == "Waffen":
        mult = (1.20 if count == 1 else 1.35) * power_ratio
        return {"multiplier": mult, "evasion": 0.0, "power_ratio": power_ratio, "desc": f"+{int((mult-1)*100)}% Lade-Tempo"}
    elif room_name == "Schild":
        mult = (1.20 if count == 1 else 1.35) * power_ratio
        return {"multiplier": mult, "evasion": 0.0, "power_ratio": power_ratio, "desc": f"+{int((mult-1)*100)}% Erholung"}
    elif room_name == "Brücke":
        ev = (0.10 if count == 1 else 0.15) * power_ratio
        desc = "+10% Ausweichen (Pilot)" if count == 1 else "+15% Ausweichen (Co-Pilot)"
        return {"multiplier": 1.0 * power_ratio, "evasion": ev, "power_ratio": power_ratio, "desc": desc}
    elif room_name == "Maschinen":
        ev = (0.05 if count == 1 else 0.10) * power_ratio
        return {"multiplier": 1.0 * power_ratio, "evasion": ev, "power_ratio": power_ratio, "desc": f"+{int(ev*100)}% Ausweichen"}
    elif room_name == "Medbay":
        mult = (1.25 if count == 1 else 1.50) * power_ratio
        return {"multiplier": mult, "evasion": 0.0, "power_ratio": power_ratio, "desc": f"+{int((mult-1)*100)}% Heilung"}
    elif room_name == "Drohnen-Kontrolle":
        mult = (1.15 if count == 1 else 1.30) * power_ratio
        return {"multiplier": mult, "evasion": 0.0, "power_ratio": power_ratio, "desc": f"+{int((mult-1)*100)}% Drohnen-Tempo"}

    return {"multiplier": 1.0 * power_ratio, "evasion": 0.0, "power_ratio": power_ratio, "desc": f"{count} Crew"}


def can_afford_choice(choice: Union[EventChoice, dict[str, Any]], player: PlayerData) -> bool:
    """Checks if player has enough resources (scrap, fuel, missiles, drones) for an event choice."""
    if not player or not choice:
        return True

    action = choice.get("action", "")
    if action == "BUY_FUEL" and getattr(player, "scrap", 0) < 10:
        return False

    req_scrap: int = int(choice.get("requires_scrap", 0))
    req_fuel: int = int(choice.get("requires_fuel", 0))
    req_missiles: int = int(choice.get("requires_missiles", 0))
    req_drones: int = int(choice.get("requires_drones", choice.get("requires_drone_parts", 0)))

    scrap_val: int = int(choice.get("scrap", 0))
    fuel_val: int = int(choice.get("fuel", 0))
    missile_val: int = int(choice.get("missiles", 0))
    drone_val: int = int(choice.get("drones", choice.get("drone_parts", 0)))

    if scrap_val < 0:
        req_scrap = max(req_scrap, abs(scrap_val))
    if fuel_val < 0:
        req_fuel = max(req_fuel, abs(fuel_val))
    if missile_val < 0:
        req_missiles = max(req_missiles, abs(missile_val))
    if drone_val < 0:
        req_drones = max(req_drones, abs(drone_val))

    if getattr(player, "scrap", 0) < req_scrap:
        return False
    if getattr(player, "fuel", 0) < req_fuel:
        return False
    if getattr(player, "missiles", 0) < req_missiles:
        return False
    if getattr(player, "drone_parts", 0) < req_drones:
        return False

    return True


def get_max_potential_damage(choice: Union[EventChoice, dict[str, Any]]) -> int:
    """Calculates the maximum potential damage a choice (or any of its outcomes) can cause to the player's ship."""
    if not choice:
        return 0
    max_dmg = int(choice.get("damage", 0))
    outcomes = choice.get("outcomes")
    if outcomes and isinstance(outcomes, list):
        for o in outcomes:
            if isinstance(o, (dict, EventChoice)):
                o_dmg = int(o.get("damage", 0))
                if o_dmg > max_dmg:
                    max_dmg = o_dmg
    return max_dmg
