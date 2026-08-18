from typing import TYPE_CHECKING

import pygame
from classes.Crew import Crew
from classes.GameData import GameData
from settings import STATE_MAP

if TYPE_CHECKING:
    from game import Game


class TrainingManager:

    def __init__(self, data: GameData):
        self.data = data
        self.game: "Game | None" = None   # Set by Game after construction
        self.btn_leave_training = pygame.Rect(320, 510, 260, 42)
        self.training_cost = 20

    def handle_click(self, mx: float, my: float):
        if self.btn_leave_training.collidepoint(mx, my):
            sm = getattr(self.game, "state_manager", None) if self.game else None
            if sm and type(sm).__name__ == "StateManager":
                sm.change_state(STATE_MAP)
            else:
                self.data.current_state = STATE_MAP
            return

        skills = ["repair", "combat", "piloting", "fitness"]
        skill_names_de = {
            "repair": "Reparatur",
            "combat": "Nahkampf",
            "piloting": "Piloten",
            "fitness": "Fitness (+HP)",
        }

        num_crew = max(1, len(self.data.player.crew))
        compact = num_crew > 4
        card_spacing = 65 if compact else 95
        upg_h = 22 if compact else 26
        upg_y_off = 28 if compact else 36

        # Prüfen ob ein Skill-Upgrade-Button eines Crew-Mitglieds angeklickt wurde
        for c_idx, crew in enumerate(self.data.player.crew):
            card_y = 98 + c_idx * card_spacing
            for s_idx, skill in enumerate(skills):
                s_box_x = 465 + s_idx * 98
                btn_rect = pygame.Rect(s_box_x + 4, card_y + 4 + upg_y_off, 84, upg_h)
                if btn_rect.collidepoint(mx, my):
                    self.buy_training(crew, skill, skill_names_de[skill])
                    return

    def buy_training(self, crew: Crew, skill_name: str, display_name: str):
        current_lvl = getattr(crew, f"skill_{skill_name}", 0)
        if current_lvl >= 3:
            self.data.combat.msg = f"{crew.name.upper()}: {display_name.upper()} BEREITS MAXIMAL (LVL 3)!"
            self.data.combat.msg_timer = 2.0
            return

        if self.data.player.scrap < self.training_cost:
            self.data.combat.msg = "NICHT GENUG SCRAP ZUM TRAINIEREN!"
            self.data.combat.msg_timer = 1.8
            return

        ach_mgr = getattr(self.game, "achievement_manager", None)
        if crew.train_skill(skill_name, ach_mgr):
            self.data.player.scrap -= self.training_cost
            new_lvl = getattr(crew, f"skill_{skill_name}", 0)
            self.data.combat.msg = f"{crew.name.upper()} HAT {display_name.upper()} AUF STUFE {new_lvl} TRAINIERT!"
            self.data.combat.msg_timer = 2.5
