import pygame

from classes.Crew import Crew
from classes.GameData import GameData
from classes.Weapon import Weapon
from settings import *


class ShopManager:

    def __init__(self, data: GameData):
        self.data = data

        self.btn_repair = pygame.Rect(200, 140, 500, 38)
        self.btn_fuel = pygame.Rect(200, 185, 500, 38)
        self.btn_missiles = pygame.Rect(200, 230, 500, 38)
        self.btn_upgrade_reactor = pygame.Rect(200, 275, 500, 38)
        self.btn_buy_crew = pygame.Rect(200, 320, 500, 38)
        self.btn_buy_weapon = pygame.Rect(200, 365, 500, 38)
        self.btn_leave_shop = pygame.Rect(200, 420, 500, 38)

    def handle_click(self, mx: float, my: float):

        if self.btn_repair.collidepoint(mx, my):
            self.buy_repair()

        elif self.btn_fuel.collidepoint(mx, my):
            self.buy_fuel()

        elif self.btn_missiles.collidepoint(mx, my):
            self.buy_missiles()

        elif self.btn_upgrade_reactor.collidepoint(mx, my):
            self.upgrade_reactor()

        elif self.btn_buy_crew.collidepoint(mx, my):
            self.buy_crew()

        elif self.btn_buy_weapon.collidepoint(mx, my):
            self.buy_weapon()

        elif self.btn_leave_shop.collidepoint(mx, my):
            self.leave_shop()
            
    def buy_repair(self):

        if self.data.player_scrap < 2:
            return

        if self.data.player_ship.hp >= self.data.player_ship.max_hp:
            return

        self.data.player_scrap -= 2
        self.data.player_ship.hp += 1
        
    def buy_fuel(self):

        if self.data.player_scrap < 3:
            return

        self.data.player_scrap -= 3
        self.data.player_fuel += 1
        
    def buy_missiles(self):

        if self.data.player_scrap < 6:
            return

        self.data.player_scrap -= 6
        self.data.player_missiles += 3
        
    def upgrade_reactor(self):

        if self.data.player_scrap < 15:
            return

        self.data.player_scrap -= 15

        self.data.player_reactor.total_power += 1
        self.data.player_reactor.available_power += 1
        
    def buy_crew(self):

        if self.data.player_scrap < 25:
            return

        self.data.player_scrap -= 25

        spawn_room = self.data.player_ship.rooms[0]

        self.data.player_crew.append(
            Crew(
                spawn_room.rect.centerx,
                spawn_room.rect.centery,
            )
        )
        
    def buy_weapon(self):

        if self.data.player_scrap < 45:
            return

        if len(self.data.player_weapons) >= 3:
            return

        self.data.player_scrap -= 45

        self.data.player_weapons.append(
            Weapon(
                "Pike Strahl",
                charge_time=5.0,
                w_type="BEAM",
                shield_pierce=1,
                damage=25.0,
            )
        )
        
    def leave_shop(self):

        self.data.current_state = STATE_MAP