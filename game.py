import sys
import pygame

from classes.GameData import GameData
from managers.combat_manager import CombatManager
from managers.input_manager import InputManager
from managers.map_manager import MapManager
from managers.render_manager import RenderManager
from managers.shop_manager import ShopManager
from managers.state_manager import StateManager
from managers.weapon_manager import WeaponManager
from settings import *


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("FTL Prototype - Erweiterte Schusslinien & Autofire")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.data = GameData()
        self.shop_manager = ShopManager(self.data)
        self.map_manager = MapManager(self.data)
        self.state_manager = StateManager(self.data)
        self.weapon_manager = WeaponManager(self.data)
        self.input_manager = InputManager(
            self.data, self.shop_manager, self.map_manager, self.weapon_manager
        )
        self.combat_manager = CombatManager(self.data, self.state_manager)
        self.render_manager = RenderManager(self.screen, self.data)

    def run(self) -> None:
        while self.data.running:
            dt = self.clock.tick(60) / 1000.0

            self.input_manager.update()
            self.combat_manager.update(dt)
            self.render_manager.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()