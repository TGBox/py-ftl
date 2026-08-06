import asyncio
import sys
import pygame

from classes.GameData import GameData
from managers.combat_manager import CombatManager
from managers.input_manager import InputManager
from managers.map_manager import MapManager
from managers.render_manager import RenderManager
from managers.shop_manager import ShopManager
from managers.sound_manager import SoundManager
from managers.state_manager import StateManager
from managers.weapon_manager import WeaponManager
from settings import *


class Game:
    def __init__(self) -> None:
        pygame.init()
        # Event Queue Überlauf-Schutz (SRS Kap. 4)
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        # Audio-Engine Konfiguration (SRS Kap. 9)
        if pygame.mixer.get_init():
            pygame.mixer.set_num_channels(32)
            pygame.mixer.set_reserved(4)

        # --- Display: logische Oberfläche + skaliertes Fenster ---
        self.resolution_idx: int = 0
        self.is_fullscreen: bool = False
        self.logical_surface: pygame.Surface = pygame.Surface(
            (LOGICAL_WIDTH, LOGICAL_HEIGHT)
        )
        self.screen: pygame.Surface = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption("FTL Clone - Pygame-CE Engine")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.data = GameData()
        self.sound = SoundManager()
        self.shop_manager = ShopManager(self.data)
        self.data.shop_manager = self.shop_manager
        self.map_manager = MapManager(self.data)
        self.state_manager = StateManager(self.data)
        self.weapon_manager = WeaponManager(self.data)
        self.input_manager = InputManager(
            self.data, self.shop_manager, self.map_manager, self.weapon_manager
        )
        self.combat_manager = CombatManager(self.data, self.state_manager)
        self.data.combat_manager = self.combat_manager
        self.render_manager = RenderManager(self.logical_surface, self.data)

        # Give managers access to sound
        self.input_manager.sound = self.sound
        self.combat_manager.sound = self.sound
        self.map_manager.sound = self.sound

        # Give managers access to the Game for display changes and state reading
        self.input_manager.game = self
        self.render_manager.game = self

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def set_resolution(self, idx: int) -> None:
        self.resolution_idx = idx % len(RESOLUTIONS)
        w, h = RESOLUTIONS[self.resolution_idx]
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((w, h))

    def toggle_fullscreen(self) -> None:
        self.is_fullscreen = not self.is_fullscreen
        w, h = RESOLUTIONS[self.resolution_idx]
        if self.is_fullscreen:
            # Use desktop resolution for fullscreen
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (info.current_w, info.current_h), pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode((w, h))

    def cycle_resolution(self) -> tuple[int, int]:
        next_idx = (self.resolution_idx + 1) % len(RESOLUTIONS)
        self.set_resolution(next_idx)
        return RESOLUTIONS[self.resolution_idx]

    def _scale_and_blit(self) -> None:
        """Scale the logical 900x600 surface to fill the actual window."""
        win_w, win_h = self.screen.get_size()
        # Maintain aspect ratio
        scale = min(win_w / LOGICAL_WIDTH, win_h / LOGICAL_HEIGHT)
        scaled_w = int(LOGICAL_WIDTH * scale)
        scaled_h = int(LOGICAL_HEIGHT * scale)
        offset_x = (win_w - scaled_w) // 2
        offset_y = (win_h - scaled_h) // 2

        # Black letterbox
        self.screen.fill((0, 0, 0))
        scaled = pygame.transform.smoothscale(
            self.logical_surface, (scaled_w, scaled_h)
        )
        self.screen.blit(scaled, (offset_x, offset_y))

    def screen_to_logical(self, mx: int, my: int) -> tuple[int, int]:
        """Convert actual screen coordinates to logical 900x600 coordinates."""
        win_w, win_h = self.screen.get_size()
        scale = min(win_w / LOGICAL_WIDTH, win_h / LOGICAL_HEIGHT)
        scaled_w = int(LOGICAL_WIDTH * scale)
        scaled_h = int(LOGICAL_HEIGHT * scale)
        offset_x = (win_w - scaled_w) // 2
        offset_y = (win_h - scaled_h) // 2
        lx = int((mx - offset_x) / scale)
        ly = int((my - offset_y) / scale)
        return lx, ly

    async def run(self) -> None:
        while self.data.running:
            dt = self.clock.tick(60) / 1000.0

            self.input_manager.update()
            self.combat_manager.update(dt)
            self.render_manager.draw()

            self._scale_and_blit()
            pygame.display.flip()

            await asyncio.sleep(0)

        pygame.quit()
        sys.exit()