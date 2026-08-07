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
from managers.training_manager import TrainingManager
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

        info = pygame.display.Info()
        self.desktop_w = info.current_w if (info and info.current_w > 0) else 1920
        self.desktop_h = info.current_h if (info and info.current_h > 0) else 1080

        self.resolutions = list(RESOLUTIONS)
        if (self.desktop_w, self.desktop_h) not in self.resolutions:
            self.resolutions.insert(0, (self.desktop_w, self.desktop_h))

        self.resolution_idx: int = self.resolutions.index((self.desktop_w, self.desktop_h))
        self.display_mode: str = "FULLSCREEN_WINDOWED"

        self.screen: pygame.Surface = None
        self.apply_display_mode()
        self.logical_surface: pygame.Surface = pygame.Surface(
            (LOGICAL_WIDTH, LOGICAL_HEIGHT)
        ).convert()
        pygame.display.set_caption("FTL Clone - Pygame-CE Engine")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.data = GameData()
        self.sound = SoundManager()
        self.shop_manager = ShopManager(self.data)
        self.data.shop_manager = self.shop_manager
        self.training_manager = TrainingManager(self.data)
        self.data.training_manager = self.training_manager
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
        if getattr(self.data, "achievements", None):
            self.data.achievements.sound = self.sound

        # Give managers access to the Game for display changes and state reading
        self.input_manager.game = self
        self.render_manager.game = self

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def apply_display_mode(self) -> None:
        """Sichere Display-Modus Umschaltung ohne SDL2-Hänger auf Windows."""
        pygame.event.pump()
        target_w, target_h = self.resolutions[self.resolution_idx]

        if self.display_mode == "FULLSCREEN_WINDOWED":
            # Rahmenloses maximiertes Fenster in nativer Desktop-Auflösung (1920x1080)
            self.screen = pygame.display.set_mode((self.desktop_w, self.desktop_h), pygame.NOFRAME)
        elif self.display_mode == "FULLSCREEN":
            # Exklusives Vollbild
            self.screen = pygame.display.set_mode((target_w, target_h), pygame.FULLSCREEN)
        else:  # "WINDOWED"
            # Skalierbares Fenster
            self.screen = pygame.display.set_mode((target_w, target_h), pygame.RESIZABLE)

        # Skalierten Ziel-Surface Cache aktualisieren
        win_w, win_h = self.screen.get_size()
        scale = min(win_w / LOGICAL_WIDTH, win_h / LOGICAL_HEIGHT)
        scaled_w = max(1, int(LOGICAL_WIDTH * scale))
        scaled_h = max(1, int(LOGICAL_HEIGHT * scale))
        self.scaled_surface = pygame.Surface((scaled_w, scaled_h)).convert()

    def cycle_display_mode(self) -> str:
        modes = ["FULLSCREEN_WINDOWED", "WINDOWED", "FULLSCREEN"]
        cur_i = modes.index(self.display_mode) if self.display_mode in modes else 0
        self.display_mode = modes[(cur_i + 1) % len(modes)]
        self.apply_display_mode()
        return self.display_mode

    def cycle_resolution(self) -> tuple[int, int]:
        self.resolution_idx = (self.resolution_idx + 1) % len(self.resolutions)
        self.apply_display_mode()
        return self.resolutions[self.resolution_idx]

    def _scale_and_blit(self) -> None:
        """Skaliert die logische 900x600 Canvas glatt und blitzschnell auf den Bildschirm."""
        win_w, win_h = self.screen.get_size()
        scale = min(win_w / LOGICAL_WIDTH, win_h / LOGICAL_HEIGHT)
        scaled_w = int(LOGICAL_WIDTH * scale)
        scaled_h = int(LOGICAL_HEIGHT * scale)
        offset_x = (win_w - scaled_w) // 2
        offset_y = (win_h - scaled_h) // 2

        # Surface Cache-Reallokation falls Fenstergröße im Windowed-Modus verändert wird
        if (
            self.scaled_surface is None
            or self.scaled_surface.get_width() != scaled_w
            or self.scaled_surface.get_height() != scaled_h
        ):
            self.scaled_surface = pygame.Surface((scaled_w, scaled_h)).convert()

        # Glatte 0.5ms Bilinear-Skalierung mit dest_surface Memory-Reusability
        pygame.transform.smoothscale(self.logical_surface, (scaled_w, scaled_h), self.scaled_surface)

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.scaled_surface, (offset_x, offset_y))

    def screen_to_logical(self, mx: int, my: int) -> tuple[int, int]:
        """Umgerechnete Mauskordinaten von Bildschirmauflösung auf 900x600."""
        win_w, win_h = self.screen.get_size()
        scale = min(win_w / LOGICAL_WIDTH, win_h / LOGICAL_HEIGHT)
        scaled_w = int(LOGICAL_WIDTH * scale)
        scaled_h = int(LOGICAL_HEIGHT * scale)
        offset_x = (win_w - scaled_w) // 2
        offset_y = (win_h - scaled_h) // 2
        lx = int((mx - offset_x) / scale)
        ly = int((my - offset_y) / scale)
        return lx, ly

    def update_audio_state(self) -> None:
        state = self.data.current_state
        if state in (STATE_MAIN_MENU, STATE_OPTIONS, STATE_ACHIEVEMENTS):
            self.sound.play_music("bgm_menu")
        elif state in (STATE_MAP, STATE_SHOP, STATE_EVENT, STATE_TRAINING):
            self.sound.play_music("bgm_explore")
        elif state == STATE_COMBAT:
            is_boss = getattr(self.data.enemy.ship, "is_boss", False) or getattr(self.data.enemy.ship, "is_miniboss", False)
            if is_boss:
                self.sound.play_music("bgm_boss")
            else:
                self.sound.play_music("bgm_combat")
        elif state in (STATE_GAME_OVER, STATE_VICTORY):
            self.sound.stop_music()

    def run(self) -> None:
        from managers.save_manager import SaveManager

        while self.data.running:
            dt = self.clock.tick(60) / 1000.0

            try:
                self.update_audio_state()
                self.input_manager.update()
                self.combat_manager.update(dt)
                self.render_manager.draw()
            except Exception as e:
                import traceback
                print(f"!!! CHIP/GAME CRASH PREVENTED: {e} !!!")
                traceback.print_exc()

                # Emergency Autosave on unexpected error
                try:
                    SaveManager.save_game(self.data)
                    print("Notfall-Spielstand erfolgreich gesichert!")
                except Exception as save_err:
                    print(f"Notfall-Speichern fehlgeschlagen: {save_err}")

                self.data.show_message(f"FEHLER VERMIEDEN: {e}")
                # Recover safely: return to MAP or MAIN_MENU if critical
                if self.data.current_state not in (STATE_MAIN_MENU, STATE_MAP):
                    self.data.current_state = STATE_MAP

            self._scale_and_blit()
            pygame.display.flip()

        pygame.quit()
        sys.exit()