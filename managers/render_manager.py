import pygame

from classes.GameData import GameData
from settings import *

class RenderManager:

    def __init__(self, screen: pygame.Surface, data: GameData):
        self.screen = screen
        self.data = data
        self.screen.fill(COLOR_BG)  #[cite: 2]
        self.font = pygame.font.SysFont(None, 24)
        self.btn_autofire = pygame.Rect(730, 310, 140, 30)
        # Shop UI Buttons
        self.btn_repair = pygame.Rect(200, 140, 500, 38)  #[cite: 1]
        self.btn_fuel = pygame.Rect(200, 185, 500, 38)  #[cite: 1]
        self.btn_missiles = pygame.Rect(200, 230, 500, 38)  #[cite: 1]
        self.btn_upgrade_reactor = pygame.Rect(200, 275, 500, 38)  #[cite: 1]
        self.btn_buy_crew = pygame.Rect(200, 320, 500, 38)  #[cite: 1]
        self.btn_buy_weapon = pygame.Rect(200, 365, 500, 38)  #[cite: 1]
        self.btn_leave_shop = pygame.Rect(200, 420, 500, 38)  #[cite: 1]

    def draw(self):

        self.screen.blit(
              self.font.render(
                  f"Treibstoff: {self.data.player_fuel}  |  Raketen: {self.data.player_missiles}  |  Scrap: {self.data.player_scrap}  |"
                  f"  Hülle: {self.data.player_ship.hp}/{self.data.player_ship.max_hp}  |  Sektor:"
                  f" {self.data.star_map.sector}",  #[cite: 12]
                  True,
                  (255, 255, 255),
              ),
              (20, 15),
          )

        if self.data.current_state == STATE_MAP:
            self.draw_map()

        elif self.data.current_state == STATE_COMBAT:
            self.draw_combat()

        elif self.data.current_state == STATE_SHOP:
            self.draw_shop()
            
    def draw_combat(self):

        self.draw_rooms()

        self.draw_projectiles()

        self.draw_shields()

        self.draw_weapons()

        self.draw_messages()
        
    def draw_map(self):
        pass        
    def draw_shop(self):
        pygame.draw.rect(self.screen, (25, 30, 40), (150, 70, 600, 430))
        pygame.draw.rect(
            self.screen, COLOR_SHOP_NODE, (150, 70, 600, 430), 3
        )  #[cite: 2]
        self.screen.blit(
            self.font.render(
                "--- HÄNDLER-STATION ---", True, COLOR_SHOP_NODE
            ),  #[cite: 2]
            (340, 90),
        )
    
        for btn, text in [
            (self.btn_repair, "Hülle reparieren (+1 HP) - 2 Scrap"),
            (self.btn_fuel, "Treibstoff kaufen (+1 Fuel) - 3 Scrap"),
            (self.btn_missiles, "Raketen kaufen (+3 Raketen) - 6 Scrap"),
            (self.btn_upgrade_reactor, "Reaktor aufrüsten (+1 Power) - 15 Scrap"),
            (self.btn_buy_crew, "Crew-Mitglied anheuern - 25 Scrap"),
            (self.btn_buy_weapon, "Strahlenwaffe (Pike) kaufen - 45 Scrap"),
        ]:
            pygame.draw.rect(self.screen, (40, 50, 70), btn)
            pygame.draw.rect(self.screen, COLOR_BORDER, btn, 2)  #[cite: 2]
            self.screen.blit(
                self.font.render(text, True, (220, 220, 220)), (btn.x + 20, btn.y + 10)
            )
    
        pygame.draw.rect(self.screen, (60, 40, 40), self.btn_leave_shop)
        pygame.draw.rect(
            self.screen, COLOR_ENEMY_BORDER, self.btn_leave_shop, 2
        )  #[cite: 2]
        self.screen.blit(
            self.font.render("Shop verlassen", True, (255, 200, 200)),
            (self.btn_leave_shop.x + 180, self.btn_leave_shop.y + 10),
        )       
    def draw_rooms(self):
        pass        
    def draw_shields(self):
        pass        
    def draw_projectiles(self):
        pass        
    def draw_weapons(self):
        pass        
    def draw_messages(self):
        pass