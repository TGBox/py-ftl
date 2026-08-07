import pygame


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """Wraps text into lines that do not exceed max_width pixels when rendered by font."""
    if not text:
        return []
    lines = []
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


def calculate_event_layout(
    ev_text: str,
    res_text: str,
    choices: list,
    font: pygame.font.Font,
    box_x: int = 120,
    box_y: int = 100,
    box_width: int = 660,
    min_box_height: int = 380,
    max_text_width: int = 600,
) -> dict:
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
    choice_rects = []
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

    for idx, choice in enumerate(choices):
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
