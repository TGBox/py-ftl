import sys
import pygame

from classes.EventManager import EventManager
from classes.GameData import GameData
from managers.achievement_manager import AchievementManager
from managers.combat_manager import CombatManager
from managers.console_manager import ConsoleManager
from managers.input_manager import InputManager
from managers.map_manager import MapManager
from managers.particle_manager import ParticleManager
from managers.render_manager import RenderManager
from managers.save_manager import SaveManager
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

        self.screen: pygame.Surface | None = None
        self.apply_display_mode()
        self.logical_surface: pygame.Surface = pygame.Surface(
            (LOGICAL_WIDTH, LOGICAL_HEIGHT)
        ).convert()
        pygame.display.set_caption("FTL Clone - Pygame-CE Engine")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.save_notification_timer: float = 0.0
        self.save_notification_msg: str = ""

        self.data: GameData = GameData()
        
        self.achievement_manager: AchievementManager = AchievementManager()
        self.combat_manager = CombatManager(self.data)
        self.console_manager = ConsoleManager(self.data)
        self.event_manager = EventManager()
        self.input_manager = InputManager(self.data)
        self.map_manager = MapManager(self.data)
        self.particle_manager: ParticleManager = ParticleManager()
        self.render_manager = RenderManager(self.logical_surface, self.data)
        self.save_manager = SaveManager()
        self.shop_manager = ShopManager(self.data)
        self.sound_manager: SoundManager = SoundManager()
        self.state_manager = StateManager(self.data)
        self.training_manager = TrainingManager(self.data)
        self.weapon_manager = WeaponManager(self.data)

        # Give managers access to sound
        self.input_manager.sound = self.sound_manager
        self.combat_manager.sound = self.sound_manager
        self.map_manager.sound = self.sound_manager
        if getattr(self.data, "achievements", None):
            self.achievement_manager.sound = self.sound_manager

        # Give managers access to the Game for display changes and state reading
        self.input_manager.game = self
        self.render_manager.game = self
        self.sound_manager.game = self
        self.achievement_manager.game = self
        self.particle_manager.game = self
        self.shop_manager.game = self
        self.training_manager.game = self
        self.map_manager.game = self
        self.state_manager.game = self
        self.weapon_manager.game = self
        self.console_manager.game = self
        self.input_manager.game = self
        self.combat_manager.game = self
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
        self.scaled_surface: pygame.Surface | None = pygame.Surface((scaled_w, scaled_h)).convert()

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
        assert self.screen is not None
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
        assert self.screen is not None
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
            self.sound_manager.play_music("bgm_menu")
        elif state in (STATE_MAP, STATE_SHOP, STATE_EVENT, STATE_TRAINING):
            s_type = getattr(self.data.world.star_map, "sector_type", "Zivil")
            if "Nebel" in s_type:
                self.sound_manager.play_music("bgm_nebula")
            elif "Piraten" in s_type or "Rebellen" in s_type:
                self.sound_manager.play_music("bgm_pirate")
            elif "Zivil" in s_type:
                self.sound_manager.play_music("bgm_civilian")
            else:
                self.sound_manager.play_music("bgm_explore")
        elif state == STATE_COMBAT:
            is_boss = getattr(self.data.enemy.ship, "is_boss", False) or getattr(self.data.enemy.ship, "is_miniboss", False)
            if is_boss:
                self.sound_manager.play_music("bgm_boss")
            else:
                self.sound_manager.play_music("bgm_combat")
        elif state in (STATE_GAME_OVER, STATE_VICTORY):
            self.sound_manager.stop_music()

    def run(self) -> None:
        from managers.save_manager import SaveManager

        while self.data.running:
            dt = self.clock.tick(60) / 1000.0

            # Pause game logic when paused or when any menu/overlay is active
            is_menu_open = (
                getattr(self.data, "show_pause_menu", False)
                or getattr(self.data, "show_help_overlay", False)
                or getattr(self.data.player, "show_crew_menu", False)
                or getattr(self.data, "show_slot_modal", False)
                or self.data.current_state in (STATE_OPTIONS, STATE_ACHIEVEMENTS)
            )
            effective_dt = 0.0 if (self.data.paused or is_menu_open) else dt
            if getattr(self.data, "turbo_mode", False):
                effective_dt *= 2.5

            try:
                self.update_audio_state()
                self.input_manager.update()
                self.combat_manager.update(effective_dt)
                self.render_manager.draw()
            except Exception as e:
                import traceback
                print(f"!!! CHIP/GAME CRASH PREVENTED: {e} !!!")
                traceback.print_exc()

                # Emergency Autosave on unexpected error
                try:
                    SaveManager.save_game(self.data, self)
                    print("Notfall-Spielstand erfolgreich gesichert!")
                except Exception as save_err:
                    print(f"Notfall-Speichern fehlgeschlagen: {save_err}")

                if hasattr(self.data, "combat"):
                    self.data.combat.msg = f"FEHLER VERMIEDEN: {e}"
                    self.data.combat.msg_timer = 4.0
                # Recover safely: return to MAP or MAIN_MENU if critical
                if self.data.current_state not in (STATE_MAIN_MENU, STATE_MAP):
                    self.data.current_state = STATE_MAP

            self._scale_and_blit()
            pygame.display.flip()

        pygame.quit()
        sys.exit()