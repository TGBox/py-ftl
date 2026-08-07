import pygame
from classes.GameData import GameData
from settings import STATE_MAP


class TrainingManager:

    def __init__(self, data: GameData):
        self.data = data
        self.btn_leave_training = pygame.Rect(320, 510, 260, 42)
        self.training_cost = 20

    def handle_click(self, mx: float, my: float):
        if self.btn_leave_training.collidepoint(mx, my):
            self.data.current_state = STATE_MAP
            return

        skills = ["repair", "combat", "piloting", "fitness"]
        skill_names_de = {
            "repair": "Reparatur",
            "combat": "Nahkampf",
            "piloting": "Piloten",
            "fitness": "Fitness (+HP)",
        }

        # Prüfen ob ein Skill-Upgrade-Button eines Crew-Mitglieds angeklickt wurde
        for c_idx, crew in enumerate(self.data.player.crew):
            card_y = 110 + c_idx * 90
            for s_idx, skill in enumerate(skills):
                btn_x = 470 + s_idx * 98
                btn_rect = pygame.Rect(btn_x, card_y + 36, 92, 28)
                if btn_rect.collidepoint(mx, my):
                    self.buy_training(crew, skill, skill_names_de[skill])
                    return

    def buy_training(self, crew, skill_name: str, display_name: str):
        current_lvl = getattr(crew, f"skill_{skill_name}", 0)
        if current_lvl >= 3:
            self.data.combat.msg = f"{crew.name.upper()}: {display_name.upper()} BEREITS MAXIMAL (LVL 3)!"
            self.data.combat.msg_timer = 2.0
            return

        if self.data.player.scrap < self.training_cost:
            self.data.combat.msg = "NICHT GENUG SCRAP ZUM TRAINIEREN!"
            self.data.combat.msg_timer = 1.8
            return

        ach_mgr = getattr(self.data, "achievements", None)
        if crew.train_skill(skill_name, ach_mgr):
            self.data.player.scrap -= self.training_cost
            new_lvl = getattr(crew, f"skill_{skill_name}", 0)
            self.data.combat.msg = f"{crew.name.upper()} HAT {display_name.upper()} AUF STUFE {new_lvl} TRAINIERT!"
            self.data.combat.msg_timer = 2.5
