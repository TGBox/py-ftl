import math
import pygame

from classes.GameData import GameData
from game import Game
from settings import *
from utils import *

class RenderManager:

    def __init__(self, screen: pygame.Surface, data: GameData):
        self.screen = screen
        self.data = data
        self.game: Game | None = None   # Set by Game after construction
        self.load_assets()
        self.small_font = pygame.font.SysFont(None, 18)
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36, bold=True)
        # Top-Right Buttons
        self.btn_crew_toggle = pygame.Rect(750, 8, 130, 26)
        self.btn_doors_open_all = pygame.Rect(750, 38, 130, 26)
        self.btn_doors_close_all = pygame.Rect(750, 68, 130, 26)
        self.btn_airlocks_vent = pygame.Rect(750, 98, 130, 26)
        self.btn_help_toggle = pygame.Rect(750, 128, 130, 26)

        # Bottom Action Buttons
        self.btn_ftl = pygame.Rect(265, 512, 140, 34)
        self.btn_repair_drone = pygame.Rect(415, 470, 140, 34)
        self.btn_combat_drone = pygame.Rect(565, 470, 140, 34)
        self.btn_cloak = pygame.Rect(715, 470, 140, 34)
        self.btn_recall = pygame.Rect(415, 512, 140, 34)
        self.btn_teleport = pygame.Rect(565, 512, 140, 34)
        self.btn_autofire = pygame.Rect(715, 512, 140, 34)

        # Shop UI Buttons
        self.btn_repair = pygame.Rect(200, 140, 500, 38)
        self.btn_fuel = pygame.Rect(200, 185, 500, 38)
        self.btn_missiles = pygame.Rect(200, 230, 500, 38)
        self.btn_upgrade_reactor = pygame.Rect(200, 275, 500, 38)
        self.btn_buy_crew = pygame.Rect(200, 320, 500, 38)
        self.btn_buy_weapon = pygame.Rect(200, 365, 500, 38)
        self.btn_leave_shop = pygame.Rect(200, 420, 500, 38)
        # Pause UI Buttons
        self.btn_pause_resume = pygame.Rect(300, 160, 300, 42)
        self.btn_pause_save = pygame.Rect(300, 215, 300, 42)
        self.btn_pause_load = pygame.Rect(300, 270, 300, 42)
        self.btn_pause_options = pygame.Rect(300, 325, 300, 42)
        self.btn_pause_main_menu = pygame.Rect(300, 380, 300, 42)
        self.btn_continue_game = pygame.Rect(300, 438, 300, 42)

    def load_assets(self):
        import os

        self.assets: dict[str, pygame.Surface] = {}
        asset_defs: dict[str, tuple[str, tuple[int, int], tuple[int, int, int] | None]] = {
            "space_bg": ("assets/space_bg.png", (LOGICAL_WIDTH, LOGICAL_HEIGHT), None),
            "main_menu_bg": ("assets/main_menu_bg.png", (LOGICAL_WIDTH, LOGICAL_HEIGHT), None),
            "kestrel_hull": ("assets/kestrel_hull.png", (450, 260), (0, 0, 0)),
            "enemy_scout": ("assets/enemy_scout.png", (340, 220), (255, 255, 255)),
        }
        for key, (path, size, colorkey) in asset_defs.items():
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                    if colorkey is not None:
                        img = img.convert_alpha()
                        w, h = img.get_size()
                        for x in range(w):
                            for y in range(h):
                                r, g, b, _a = img.get_at((x, y))
                                if colorkey == (0, 0, 0) and r < 35 and g < 35 and b < 35:
                                    img.set_at((x, y), (0, 0, 0, 0))
                                elif colorkey == (255, 255, 255) and r > 220 and g > 220 and b > 220:
                                    img.set_at((x, y), (255, 255, 255, 0))
                    else:
                        img = img.convert_alpha()

                    if size:
                        img = pygame.transform.scale(img, size)
                    self.assets[key] = img
                except Exception as e:
                    print(f"Fehler beim Laden von {path}: {e}")

    def draw(self):
        if "space_bg" in self.assets and self.data.current_state not in (STATE_MAIN_MENU, STATE_OPTIONS):
            self.screen.blit(self.assets["space_bg"], (0, 0))
        else:
            self.screen.fill(COLOR_BG)

        # Top Status Banner (Rohstoffe & Sektor)
        if self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY):
            b_rect = pygame.Rect(10, 6, 735, 24)
            b_surf = pygame.Surface((b_rect.width, b_rect.height), pygame.SRCALPHA)
            b_surf.fill((12, 20, 35, 210))
            self.screen.blit(b_surf, (b_rect.x, b_rect.y))
            pygame.draw.rect(self.screen, (0, 200, 255), b_rect, 1)

            status_str = (
                f"Treibstoff: {self.data.player.fuel}  |  Raketen: {self.data.player.missiles}  |  "
                f"Drohnen: {getattr(self.data.player, 'drone_parts', 5)}  |  Scrap: {self.data.player.scrap}  |  "
                f"Sektor: {self.data.world.star_map.sector} ({self.data.world.star_map.sector_type})"
            )
            lbl = pygame.font.SysFont(None, 20).render(status_str, True, (240, 245, 255))
            self.screen.blit(lbl, (b_rect.x + 10, b_rect.y + 4))

            # Buttons oben rechts (Sci-Fi Glassmorphism Style)
            mx, my = self._logical_mouse_pos()

            self.draw_scifi_button(self.btn_crew_toggle, "Crew-Menü", is_hovered=self.btn_crew_toggle.collidepoint(mx, my), primary_color=(0, 180, 255))
            self.draw_scifi_button(self.btn_doors_open_all, "Türen auf [O]", is_hovered=self.btn_doors_open_all.collidepoint(mx, my), primary_color=(0, 220, 130))
            self.draw_scifi_button(self.btn_doors_close_all, "Türen zu [L]", is_hovered=self.btn_doors_close_all.collidepoint(mx, my), primary_color=(230, 80, 80))
            self.draw_scifi_button(self.btn_airlocks_vent, "Vakuum [V]", is_hovered=self.btn_airlocks_vent.collidepoint(mx, my), primary_color=(0, 200, 220))
            self.draw_scifi_button(self.btn_help_toggle, "[?] HILFE [H]", is_hovered=self.btn_help_toggle.collidepoint(mx, my), primary_color=(180, 120, 255))

        if self.data.current_state in (STATE_MAIN_MENU, STATE_OPTIONS) and not self.data.paused:
            self.draw_main_menu()

        elif self.data.current_state == STATE_MAP:
            self.draw_map()

        elif self.data.current_state == STATE_EVENT:
            self.draw_event()

        elif self.data.current_state == STATE_COMBAT:
            self.draw_combat()

        elif self.data.current_state == STATE_SHOP:
            self.draw_shop()

        elif self.data.current_state == STATE_TRAINING:
            self.draw_training()

        elif self.data.current_state == STATE_GAME_OVER:
            self.draw_game_over()

        elif self.data.current_state == STATE_VICTORY:
            self.draw_victory()

        elif self.data.current_state == STATE_ACHIEVEMENTS:
            self.draw_achievements_screen()

        if getattr(self.data.player, "show_crew_menu", False):
            self.draw_crew_menu()

        # Toast Notifications
        if hasattr(self.data, "achievements"):
            self.game.achievement_manager.update_toasts(0.016)
            self.game.achievement_manager.draw_toasts(self.screen, self.font)

        # In-Game Speichern-Benachrichtigung (HUD Toast)
        save_timer = getattr(self.game, "save_notification_timer", 0.0)
        if save_timer > 0.0:
            self.game.save_notification_timer = max(0.0, save_timer - 0.016)
            msg = getattr(self.data, "save_notification_msg", "SPIELSTAND GESPEICHERT")
            badge_rect = pygame.Rect(LOGICAL_WIDTH // 2 - 165, 34, 330, 24)
            pygame.draw.rect(self.screen, (10, 45, 30), badge_rect)
            pygame.draw.rect(self.screen, (0, 255, 180), badge_rect, 2)
            save_lbl = pygame.font.SysFont(None, 16, bold=True).render(f"[SAVE]  {msg}", True, (150, 255, 200))
            self.screen.blit(save_lbl, (badge_rect.x + (badge_rect.width - save_lbl.get_width()) // 2, badge_rect.y + 4))

        # Taktische Pause Banner (SPACE)
        if self.data.paused and not getattr(self.data, "show_pause_menu", False):
            banner_rect = pygame.Rect(245, 34, 265, 22)
            pygame.draw.rect(self.screen, (30, 40, 60), banner_rect)
            pygame.draw.rect(self.screen, (255, 220, 100), banner_rect, 1)
            p_lbl = pygame.font.SysFont(None, 16, bold=True).render("--- PAUSE (TAKTISCHER MODUS) ---", True, (255, 255, 100))
            self.screen.blit(p_lbl, (banner_rect.x + (banner_rect.width - p_lbl.get_width()) // 2, banner_rect.y + 4))

        # Pause-Menü Modal (ESC)
        if getattr(self.data, "show_pause_menu", False):
            if self.data.current_state == STATE_OPTIONS:
                self.draw_options_menu()
            else:
                self.draw_pause_menu()

        # Hilfe-Overlay Modal (H / F1)
        if getattr(self.data, "show_help_overlay", False):
            self.draw_help_overlay()

        # 3 Save Slots Selector Modal
        if getattr(self.data, "show_slot_modal", False):
            self.draw_save_load_slot_modal()

        # Ingame Developer Console Overlay (TODO 43)
        console_mgr = getattr(self, "console_manager", None) or getattr(self.data, "console_manager", None)
        if console_mgr:
            console_mgr.render(self.screen)

    def draw_save_load_slot_modal(self):
        overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 230))
        self.screen.blit(overlay, (0, 0))

        modal_rect = pygame.Rect(160, 50, 580, 490)
        pygame.draw.rect(self.screen, (20, 30, 45), modal_rect)
        pygame.draw.rect(self.screen, (0, 200, 255), modal_rect, 3)

        mode = getattr(self.data, "slot_modal_mode", "SAVE")
        title = "--- SPIELSTAND SPEICHERN (SLOT 1 - 3) ---" if mode == "SAVE" else "--- SPIELSTAND LADEN (SLOT 1 - 3) ---"
        title_txt = self.font.render(title, True, (100, 220, 255))
        self.screen.blit(title_txt, (modal_rect.x + (modal_rect.width - title_txt.get_width()) // 2, modal_rect.y + 16))

        from managers.save_manager import SaveManager
        mx, my = self._logical_mouse_pos()

        for slot in (1, 2, 3):
            card_y = modal_rect.y + 52 + (slot - 1) * 118
            card_rect = pygame.Rect(modal_rect.x + 20, card_y, 540, 106)
            info: SaveManager = SaveManager.get_slot_info(slot) # TODO: This needs to get typed correctly! And Manager should get moved to Game object!
            is_active_slot = getattr(self.data, "active_save_slot", 1) == slot

            bg_col = (30, 55, 80) if is_active_slot else (25, 35, 50)
            border_col = (0, 230, 180) if is_active_slot else (80, 120, 160)
            pygame.draw.rect(self.screen, bg_col, card_rect)
            pygame.draw.rect(self.screen, border_col, card_rect, 2)

            slot_head = f"SLOT {slot}" + ("  [AKTIV]" if is_active_slot else "")
            self.screen.blit(self.font.render(slot_head, True, (255, 220, 100) if is_active_slot else (180, 210, 240)), (card_rect.x + 15, card_rect.y + 10))

            if info:
                line1 = f"Schiff: {info['ship_name']}  |  Sektor {info['sector']} ({info['sector_type']})"
                line2 = f"Hülle: {info['hp']}  |  Scrap: {info['scrap']}  |  Zeit: {info['time_str']}"
                self.screen.blit(self.small_font.render(line1, True, (200, 235, 255)), (card_rect.x + 15, card_rect.y + 38))
                self.screen.blit(self.small_font.render(line2, True, (160, 200, 230)), (card_rect.x + 15, card_rect.y + 60))
            else:
                self.screen.blit(self.small_font.render("[ LEERER SPEICHERSLOT ]", True, (140, 155, 175)), (card_rect.x + 15, card_rect.y + 48))

            # Action Button inside slot card
            btn_rect = pygame.Rect(card_rect.x + 345, card_rect.y + 48, 180, 42)
            btn_attr = f"btn_slot_{slot}"
            setattr(self, btn_attr, btn_rect)

            btn_label = f"In Slot {slot} sichern" if mode == "SAVE" else f"Slot {slot} laden"
            btn_color = (0, 220, 130) if mode == "SAVE" else (0, 180, 255)
            self.draw_scifi_button(
                btn_rect,
                btn_label,
                is_hovered=btn_rect.collidepoint(mx, my),
                primary_color=btn_color,
                enabled=(mode == "SAVE" or info is not None)
            )

        # Close Modal Button
        self.btn_close_slot_modal = pygame.Rect(modal_rect.x + 190, modal_rect.y + 425, 200, 42)
        self.draw_scifi_button(
            self.btn_close_slot_modal,
            "ABBRECHEN",
            is_hovered=self.btn_close_slot_modal.collidepoint(mx, my),
            primary_color=(230, 80, 80)
        )

    def draw_help_overlay(self):
        overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 220))
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect(120, 50, 660, 440)
        pygame.draw.rect(self.screen, (20, 30, 45), box)
        pygame.draw.rect(self.screen, (100, 200, 255), box, 2)

        title_font = pygame.font.SysFont(None, 24, bold=True)
        head = title_font.render("❓ TASTATUR-STEUERUNG & ANLEITUNG (QUICKHELP)", True, (255, 220, 100))
        self.screen.blit(head, (box.centerx - head.get_width() // 2, box.y + 15))

        font = pygame.font.SysFont(None, 15)
        bold_font = pygame.font.SysFont(None, 15, bold=True)

        col1_x = box.x + 30
        col2_x = box.x + 350
        y = box.y + 55

        # Spalte 1: Kampf & Schiff
        lbl1 = bold_font.render("KAMPF & SYSTEM-STEUERUNG:", True, (100, 220, 255))
        self.screen.blit(lbl1, (col1_x, y))
        y += 24

        controls_col1 = [
            ("LEERTASTE", "Taktische Pause (Befehle erteilen)"),
            ("ESC", "Hauptmenü / Speichern"),
            ("H / F1", "Hilfe-Overlay (AN / AUS)"),
            ("1 - 5", "Waffen-Slot anwählen"),
            ("A", "Auto-Feuer Umschalten"),
            ("B", "Enter-Trupp entsenden (Teleport)"),
            ("R", "Enter-Trupp zurückbeamen"),
            ("C", "Tarnung (Cloaking) aktivieren"),
            ("K", "Kampfdrohne starten / stoppen"),
            ("D", "Reparaturdrohne starten / stoppen"),
        ]

        for key, desc in controls_col1:
            k_lbl = bold_font.render(key, True, (255, 200, 100))
            d_lbl = font.render(desc, True, (220, 230, 240))
            self.screen.blit(k_lbl, (col1_x, y))
            self.screen.blit(d_lbl, (col1_x + 95, y))
            y += 20

        # Spalte 2: Türen & Tipps
        y2 = box.y + 55
        lbl2 = bold_font.render("TÜR- & RAUM-STEUERUNG:", True, (100, 220, 255))
        self.screen.blit(lbl2, (col2_x, y2))
        y2 += 24

        controls_col2 = [
            ("O", "Alle Innentüren öffnen"),
            ("L", "Alle Innentüren schließen"),
            ("V", "Luftschleusen ins Weltall öffnen"),
            ("TAB", "Tür-Steuerung Schnellschalter"),
        ]

        for key, desc in controls_col2:
            k_lbl = bold_font.render(key, True, (255, 200, 100))
            d_lbl = font.render(desc, True, (220, 230, 240))
            self.screen.blit(k_lbl, (col2_x, y2))
            self.screen.blit(d_lbl, (col2_x + 65, y2))
            y2 += 20

        y2 += 15
        tips_lbl = bold_font.render("ÜBERLEBENS-TIPPS:", True, (100, 255, 150))
        self.screen.blit(tips_lbl, (col2_x, y2))
        y2 += 24

        tips = [
            "• Feuer löschen: Öffne Luftschleusen (V), um",
            "  Räume ins Vakuum zu entlüften!",
            "• Waffen-Vorheizer: Kaufe den Vorheizer im Shop",
            "  für 100% Ladung zu Kampfbeginn!",
            "• Schiffe kapern: Eliminiere die gegnerische Crew",
            "  per Entern für 35+ Scrap Extra-Beute!",
        ]

        for tip in tips:
            t_lbl = font.render(tip, True, (200, 230, 210))
            self.screen.blit(t_lbl, (col2_x, y2))
            y2 += 18

        close_lbl = font.render("Drücke H, F1 oder klicke den [?] Button zum Schließen", True, (180, 190, 200))
        self.screen.blit(close_lbl, (box.centerx - close_lbl.get_width() // 2, box.bottom - 25))

    def draw_crew_menu(self):
        pygame.draw.rect(self.screen, (25, 35, 50), (140, 60, 620, 460))
        pygame.draw.rect(self.screen, (100, 200, 255), (140, 60, 620, 460), 3)

        self.screen.blit(
            self.font.render("--- CREW-MANAGEMENT & SPEZIES-INFOS ---", True, (100, 220, 255)),
            (290, 80),
        )

        for idx, crew in enumerate(self.data.player.crew):
            card_y = 130 + idx * 75
            card_rect = pygame.Rect(170, card_y, 560, 65)
            pygame.draw.rect(self.screen, (40, 55, 75), card_rect)
            pygame.draw.rect(self.screen, (80, 100, 130), card_rect, 2)

            hp_lbl = self.font.render(f"HP: {int(crew.hp)}/{int(crew.max_hp)}", True, (100, 255, 100))

            if self.data.player.active_rename_idx == idx:
                input_rect = pygame.Rect(190, card_y + 8, 160, 24)
                pygame.draw.rect(self.screen, (20, 30, 45), input_rect)
                pygame.draw.rect(self.screen, (100, 220, 255), input_rect, 2)
                cur_text = self.data.player.rename_buffer + "|"
                self.screen.blit(self.font.render(cur_text, True, (255, 255, 100)), (input_rect.x + 5, input_rect.y + 3))
                self.screen.blit(self.font.render("[ Enter = Bestätigen ]", True, (150, 220, 150)), (360, card_y + 10))
            else:
                name_lbl = self.font.render(f"{crew.name} ({crew.species})", True, (255, 255, 255))
                self.screen.blit(name_lbl, (190, card_y + 10))
                self.screen.blit(hp_lbl, (360, card_y + 10))

            if crew.species == "Engi":
                perk_str = f"Perk [{crew.trait}]: +100% Reparieren, -50% Kampf"
                badge_col = (255, 180, 50)
            elif crew.species == "Mantis":
                perk_str = f"Perk [{crew.trait}]: +50% Kampf, -40% Reparieren"
                badge_col = (80, 240, 80)
            else:
                perk_str = f"Perk [{crew.trait}]: Ausgewogene Standardwerte"
                badge_col = (100, 180, 255)

            perk_lbl = self.font.render(perk_str, True, badge_col)

            # Umbenennen Button
            rename_btn = pygame.Rect(580, card_y + 15, 130, 35)
            btn_col = (100, 140, 60) if self.data.player.active_rename_idx == idx else (60, 80, 110)
            pygame.draw.rect(self.screen, btn_col, rename_btn)
            pygame.draw.rect(self.screen, COLOR_BORDER, rename_btn, 1)
            btn_txt = "Tippen..." if self.data.player.active_rename_idx == idx else "Umbenennen"
            self.screen.blit(self.font.render(btn_txt, True, (220, 240, 255)), (rename_btn.x + 12, rename_btn.y + 8))

            skills_str = f"Skills: Rep Lvl {crew.skill_repair}/3 | Dmg Lvl {crew.skill_combat}/3 | Nav Lvl {crew.skill_piloting}/3 | Fit Lvl {crew.skill_fitness}/3"
            small_font = pygame.font.SysFont(None, 14, bold=True)
            skills_lbl = small_font.render(skills_str, True, (160, 230, 255))

            self.screen.blit(perk_lbl, (190, card_y + 30))
            self.screen.blit(skills_lbl, (190, card_y + 46))

        close_btn = pygame.Rect(370, 465, 160, 38)
        pygame.draw.rect(self.screen, (70, 40, 40), close_btn)
        pygame.draw.rect(self.screen, COLOR_ENEMY_BORDER, close_btn, 2)
        self.screen.blit(self.font.render("Schließen", True, (255, 200, 200)), (close_btn.x + 40, close_btn.y + 10))


            
    def draw_combat(self):

        is_enemy_destroyed = (self.data.enemy.ship.hp <= 0) or getattr(self.data.combat, "combat_won", False)

        # Triebwerks-Partikel dynamisch am Heck (Unterseite) der Schiffe emittieren (nach unten)
        if hasattr(self.data, "particle_manager"):
            if self.data.player.ship.rooms:
                p_left = min(r.rect.left for r in self.data.player.ship.rooms)
                p_right = max(r.rect.right for r in self.data.player.ship.rooms)
                p_bottom = max(r.rect.bottom for r in self.data.player.ship.rooms)
                p_w = p_right - p_left
                self.game.particle_manager.emit_thruster(p_left + int(p_w * 0.35), p_bottom + 6, direction_x=0.0, direction_y=1.0)
                self.game.particle_manager.emit_thruster(p_left + int(p_w * 0.65), p_bottom + 6, direction_x=0.0, direction_y=1.0)

            if not is_enemy_destroyed and self.data.enemy.ship.rooms:
                e_left = min(r.rect.left for r in self.data.enemy.ship.rooms)
                e_right = max(r.rect.right for r in self.data.enemy.ship.rooms)
                e_bottom = max(r.rect.bottom for r in self.data.enemy.ship.rooms)
                e_w = e_right - e_left
                self.game.particle_manager.emit_thruster(e_left + int(e_w * 0.35), e_bottom + 6, direction_x=0.0, direction_y=1.0)
                self.game.particle_manager.emit_thruster(e_left + int(e_w * 0.65), e_bottom + 6, direction_x=0.0, direction_y=1.0)

        self.draw_rooms()

        self.draw_projectiles()

        if hasattr(self.game, "particle_manager"):
            self.game.particle_manager.draw(self.screen)

        self.draw_shields()

        self.draw_weapons()

        self.draw_messages()
        
    def draw_map(self):
        self.data.world.star_map.draw(self.screen)       
    def draw_shop(self):
        shop_mgr = getattr(self.game, "shop_manager", None) or getattr(self.data, "shop_manager", None)
        pygame.draw.rect(self.screen, (16, 24, 38), (60, 45, 780, 510))
        pygame.draw.rect(self.screen, COLOR_SHOP_NODE, (60, 45, 780, 510), 2)

        # 1. Titel & Statusleiste oben (sauber getrennt ohne Überlappungen)
        title_font = pygame.font.SysFont(None, 24, bold=True)
        sub_font = pygame.font.SysFont(None, 16)
        tiny_font = pygame.font.SysFont(None, 14)

        t_lbl = title_font.render("--- HÄNDLER-STATION ---", True, COLOR_SHOP_NODE)
        self.screen.blit(t_lbl, (LOGICAL_WIDTH // 2 - t_lbl.get_width() // 2, 50))

        p_hp = self.data.player.ship.hp
        p_max_hp = self.data.player.ship.max_hp
        p_drones = getattr(self.data.player, "drone_parts", 5)
        status_txt = f"Dein Scrap: {self.data.player.scrap} Scrap  |  Hülle: {p_hp}/{p_max_hp} HP  |  Fuel: {self.data.player.fuel}  |  Raketen: {self.data.player.missiles}  |  Drohnen: {p_drones}"
        st_lbl = sub_font.render(status_txt, True, (255, 220, 100))
        self.screen.blit(st_lbl, (LOGICAL_WIDTH // 2 - st_lbl.get_width() // 2, 72))

        mx, my = self._logical_mouse_pos()
        active_tab = getattr(shop_mgr, "active_tab", "RESOURCES") if shop_mgr else "RESOURCES"

        # 2. Tab-Leiste (4 Kategoriereiter bei y=96)
        tabs = [
            ("RESOURCES", getattr(shop_mgr, "tab_resources", pygame.Rect(75, 96, 170, 28)), "1. RESSOURCEN"),
            ("WEAPONS", getattr(shop_mgr, "tab_weapons", pygame.Rect(255, 96, 170, 28)), "2. WAFFEN"),
            ("CREW", getattr(shop_mgr, "tab_crew", pygame.Rect(435, 96, 170, 28)), "3. CREW & ANHEUERN"),
            ("ROOMS", getattr(shop_mgr, "tab_rooms", pygame.Rect(615, 96, 170, 28)), "4. RAUM-HANDEL"),
        ]

        for tab_key, tab_rect, tab_label in tabs:
            is_active = (active_tab == tab_key)
            is_hov = tab_rect.collidepoint(mx, my)
            bg_col = (40, 60, 95) if is_active else ((30, 42, 65) if is_hov else (20, 28, 42))
            border_col = (0, 220, 255) if (is_active or is_hov) else (60, 80, 110)
            pygame.draw.rect(self.screen, bg_col, tab_rect)
            pygame.draw.rect(self.screen, border_col, tab_rect, 2 if is_active else 1)
            t_lbl = sub_font.render(tab_label, True, (255, 255, 255) if (is_active or is_hov) else (170, 190, 215))
            self.screen.blit(t_lbl, (tab_rect.x + (tab_rect.width - t_lbl.get_width()) // 2, tab_rect.y + 7))

        pygame.draw.line(self.screen, (40, 60, 90), (80, 128), (820, 128), 1)

        # ----------------------------------------------------
        # TAB 1: RESSOURCEN & REAKTOR
        # ----------------------------------------------------
        if active_tab == "RESOURCES":
            hdr_left = sub_font.render("SCHIFFS-REPARATUR & VORRÄTE:", True, (100, 220, 255))
            self.screen.blit(hdr_left, (100, 138))

            r_total = self.data.player.reactor.total_power
            r_max_needed = sum(r.max_power for r in self.data.player.ship.rooms)
            r_cap_txt = f" (Max Kapazität: {r_max_needed} Power)" if r_total >= r_max_needed else ""

            items_left = [
                (getattr(shop_mgr, "btn_repair", pygame.Rect(100, 160, 360, 32)), f"Hülle reparieren (+1 HP) - 2 Scrap (Aktuell: {p_hp}/{p_max_hp})"),
                (getattr(shop_mgr, "btn_fuel", pygame.Rect(100, 205, 360, 32)), f"Treibstoff kaufen (+1 Fuel) - 3 Scrap"),
                (getattr(shop_mgr, "btn_missiles", pygame.Rect(100, 250, 360, 32)), f"Raketen kaufen (+3 Raketen) - 6 Scrap"),
                (getattr(shop_mgr, "btn_drone_parts", pygame.Rect(100, 295, 360, 32)), f"Drohnenteile kaufen (+2 Drohnen) - 6 Scrap"),
                (getattr(shop_mgr, "btn_upgrade_reactor", pygame.Rect(100, 340, 360, 32)), f"Reaktor aufrüsten (+1 Power) - 15 Scrap ({r_total}/{r_max_needed}){r_cap_txt}"),
            ]

            for btn, text in items_left:
                is_hov = btn.collidepoint(mx, my)
                pygame.draw.rect(self.screen, (30, 45, 68) if is_hov else (22, 32, 48), btn)
                pygame.draw.rect(self.screen, (100, 200, 255) if is_hov else COLOR_BORDER, btn, 1)
                lbl = sub_font.render(text, True, (255, 255, 255) if is_hov else (210, 225, 245))
                self.screen.blit(lbl, (btn.x + 12, btn.y + 8))

            # Reaktor-Info Infobox rechts
            info_box = pygame.Rect(490, 160, 310, 212)
            pygame.draw.rect(self.screen, (20, 30, 46), info_box)
            pygame.draw.rect(self.screen, (60, 90, 130), info_box, 1)
            self.screen.blit(sub_font.render("REAKTOR-STATUS & ENERGIEBEDARF:", True, (255, 220, 100)), (505, 172))
            self.screen.blit(tiny_font.render(f"Aktuelle Reaktorleistung: {r_total} Power", True, (200, 230, 255)), (505, 200))
            self.screen.blit(tiny_font.render(f"Max. Energiebedarf aller Räume: {r_max_needed} Power", True, (200, 230, 255)), (505, 222))

            if r_total >= r_max_needed:
                self.screen.blit(tiny_font.render("STATUS: Reaktor voll für alle Schiffsräume ausgebaut!", True, (100, 255, 160)), (505, 250))
            else:
                self.screen.blit(tiny_font.render(f"STATUS: Noch {r_max_needed - r_total} Reaktor-Upgrades möglich.", True, (255, 200, 100)), (505, 250))

        # ----------------------------------------------------
        # TAB 2: WAFFEN & AUGMENTATIONEN
        # ----------------------------------------------------
        elif active_tab == "WEAPONS":
            hdr_right = sub_font.render("WAFFEN & AUGMENTATIONEN IM KATALOG:", True, (255, 220, 100))
            self.screen.blit(hdr_right, (470, 136))

            catalog = getattr(shop_mgr, "catalog_stock", []) if shop_mgr else []
            for idx, item in enumerate(catalog):
                item_btn = pygame.Rect(470, 155 + idx * 56, 350, 52)
                is_hov = item_btn.collidepoint(mx, my)
                pygame.draw.rect(self.screen, (35, 55, 80) if is_hov else (24, 38, 58), item_btn)
                pygame.draw.rect(self.screen, (0, 220, 255) if is_hov else (80, 140, 190), item_btn, 1)

                if item.get("type") == "AUGMENT":
                    name_lbl = sub_font.render(f"{item['name']} (AUGMENT)", True, (240, 240, 255))
                    stats_lbl = tiny_font.render(item.get("desc", ""), True, (180, 220, 240))
                else:
                    w_type = item.get("w_type", "WEAPON")
                    sub = item.get("subtype", "STANDARD")
                    sub_tag = f" [{sub}]" if sub != "STANDARD" else ""
                    name_lbl = sub_font.render(f"{item['name']} ({w_type}){sub_tag}", True, (240, 240, 255))
                    eff_txt = f"Dmg: {int(item.get('damage', 0))} | Pierce: {item.get('shield_pierce', 0)} | Ladezeit: {item.get('charge_time', 0)}s"
                    stats_lbl = tiny_font.render(eff_txt, True, (170, 210, 235))

                price_badge = pygame.Rect(item_btn.x + item_btn.width - 85, item_btn.y + 12, 75, 26)
                pygame.draw.rect(self.screen, (50, 40, 20), price_badge)
                pygame.draw.rect(self.screen, (255, 215, 0), price_badge, 1)
                price_lbl = sub_font.render(f"{item['price']} Scrap", True, (255, 220, 100))
                self.screen.blit(price_lbl, (price_badge.x + (price_badge.width - price_lbl.get_width()) // 2, price_badge.y + 5))

                self.screen.blit(name_lbl, (item_btn.x + 10, item_btn.y + 6))
                self.screen.blit(stats_lbl, (item_btn.x + 10, item_btn.y + 28))

            # Layout Umbau Button
            btn_layout = getattr(shop_mgr, "btn_edit_layout", pygame.Rect(100, 136, 340, 36))
            is_lay_hov = btn_layout.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (45, 35, 65) if is_lay_hov else (30, 22, 48), btn_layout)
            pygame.draw.rect(self.screen, (180, 120, 255) if is_lay_hov else (110, 70, 180), btn_layout, 1)
            self.screen.blit(sub_font.render("Schiff-Layout umbauen (15 Scrap)", True, (230, 200, 255)), (btn_layout.x + 12, btn_layout.y + 9))

            # Untere Sektion: Eingebaute Waffen & Verkaufen
            pygame.draw.line(self.screen, (40, 60, 90), (80, 345), (820, 345), 1)
            hdr_weapons = sub_font.render("EINGEBAUTE WAFFEN (Klick zum Verkaufen für 50% Scrap):", True, (200, 220, 255))
            self.screen.blit(hdr_weapons, (80, 352))

            max_slots = getattr(self.data.player.ship, "max_weapons", 3)
            slots = getattr(self.data.player.ship, "weapon_slots", [])
            card_w = (740 - (max_slots - 1) * 12) // max_slots

            for idx in range(max_slots):
                card_x = 80 + idx * (card_w + 12)
                card_rect = pygame.Rect(card_x, 372, card_w, 68)
                pygame.draw.rect(self.screen, (22, 32, 48), card_rect)
                pygame.draw.rect(self.screen, COLOR_BORDER, card_rect, 1)

                slot_info = slots[idx] if idx < len(slots) else {}
                allowed = slot_info.get("allowed_types")
                allowed_txt = ", ".join(allowed) if allowed else "Alle"

                w = self.data.player.weapons[idx] if idx < len(self.data.player.weapons) else None
                if w is not None:
                    w_sub = getattr(w, "subtype", "STANDARD")
                    w_sub_tag = f" [{w_sub}]" if w_sub != "STANDARD" else ""
                    refund = max(15, 15 * w.level)

                    lbl_name = sub_font.render(f"Slot {idx+1}: {w.name}{w_sub_tag}", True, (100, 255, 180))
                    lbl_allow = tiny_font.render(f"Erlaubt: {allowed_txt}", True, (150, 175, 200))
                    self.screen.blit(lbl_name, (card_rect.x + 8, card_rect.y + 6))
                    self.screen.blit(lbl_allow, (card_rect.x + 8, card_rect.y + 24))

                    sell_btn = pygame.Rect(card_rect.x + 6, card_rect.y + 42, card_w - 12, 20)
                    is_sell_hov = sell_btn.collidepoint(mx, my)
                    pygame.draw.rect(self.screen, (100, 45, 45) if is_sell_hov else (60, 32, 32), sell_btn)
                    pygame.draw.rect(self.screen, (255, 100, 100), sell_btn, 1)
                    lbl_sell = tiny_font.render(f"Verkaufen (+{refund} Scrap)", True, (255, 200, 200))
                    self.screen.blit(lbl_sell, (sell_btn.x + (sell_btn.width - lbl_sell.get_width()) // 2, sell_btn.y + 3))
                else:
                    lbl_empty = sub_font.render(f"Slot {idx+1}: [ LEER ]", True, (140, 150, 165))
                    lbl_allow = tiny_font.render(f"Erlaubt: {allowed_txt}", True, (150, 175, 200))
                    self.screen.blit(lbl_empty, (card_rect.x + 8, card_rect.y + 12))
                    self.screen.blit(lbl_allow, (card_rect.x + 8, card_rect.y + 35))

        # ----------------------------------------------------
        # TAB 3: CREW & VORANSICHT (TODO 37)
        # ----------------------------------------------------
        elif active_tab == "CREW":
            hdr_crew = sub_font.render("NÄCHSTES CREW-MITGLIED ZUM ANHEUERN (VORSCHAU):", True, (100, 255, 180))
            self.screen.blit(hdr_crew, (100, 138))

            cand = getattr(shop_mgr, "next_crew_candidate", None) or {"name": "Rekrut #1", "species": "Mensch", "price": 25, "perks": "Allrounder"}
            card_box = pygame.Rect(100, 160, 340, 170)
            pygame.draw.rect(self.screen, (25, 40, 60), card_box)
            pygame.draw.rect(self.screen, (0, 220, 255), card_box, 2)

            spec_color = {"Mensch": (255, 220, 100), "Engi": (100, 220, 255), "Mantis": (255, 100, 100), "Rock": (220, 150, 80), "Zoltan": (120, 255, 120)}.get(cand['species'], (255, 255, 255))
            self.screen.blit(title_font.render(f"{cand['name']} ({cand['species']})", True, spec_color), (115, 175))
            self.screen.blit(sub_font.render(f"Anheuer-Preis: {cand['price']} Scrap", True, (255, 215, 0)), (115, 205))
            self.screen.blit(tiny_font.render(f"Eigenschaft: {cand['perks']}", True, (200, 225, 245)), (115, 235))

            btn_buy_c = getattr(shop_mgr, "btn_buy_crew", pygame.Rect(100, 350, 340, 44))
            is_c_hov = btn_buy_c.collidepoint(mx, my)
            pygame.draw.rect(self.screen, (0, 150, 90) if is_c_hov else (0, 100, 60), btn_buy_c)
            pygame.draw.rect(self.screen, (0, 255, 160) if is_c_hov else (0, 180, 100), btn_buy_c, 2)
            c_btn_lbl = title_font.render(f"Rekrutieren ({cand['price']} Scrap)", True, (255, 255, 255))
            self.screen.blit(c_btn_lbl, (btn_buy_c.x + (btn_buy_c.width - c_btn_lbl.get_width()) // 2, btn_buy_c.y + 10))

            # Aktuelle Crew-Liste auf der rechten Seite
            hdr_curr = sub_font.render("AKTUELLE SCHIFFS-CREW:", True, (255, 220, 100))
            self.screen.blit(hdr_curr, (480, 138))
            for idx, c in enumerate(self.data.player.crew):
                c_rect = pygame.Rect(480, 160 + idx * 48, 320, 40)
                pygame.draw.rect(self.screen, (22, 32, 48), c_rect)
                pygame.draw.rect(self.screen, (60, 90, 130), c_rect, 1)
                s_col = {"Mensch": (255, 220, 100), "Engi": (100, 220, 255), "Mantis": (255, 100, 100), "Rock": (220, 150, 80), "Zoltan": (120, 255, 120)}.get(c.species, (255, 255, 255))
                self.screen.blit(sub_font.render(f"{c.name} ({c.species})", True, s_col), (c_rect.x + 10, c_rect.y + 6))
                self.screen.blit(tiny_font.render(f"HP: {int(c.hp)}/{int(c.max_hp)}  |  Skill: {c.trait}", True, (180, 200, 220)), (c_rect.x + 10, c_rect.y + 22))

        # ----------------------------------------------------
        # TAB 4: RAUM-HANDEL (TODO 50)
        # ----------------------------------------------------
        elif active_tab == "ROOMS":
            from managers.shop_manager import SYSTEM_ROOM_CATALOG, PROTECTED_CORE_SYSTEMS

            hdr_buy_sys = sub_font.render("NEUE SYSTEME FÜR LEERE RAUM-SLOTS KAUFEN:", True, (100, 255, 180))
            self.screen.blit(hdr_buy_sys, (100, 138))

            for idx, sys_item in enumerate(SYSTEM_ROOM_CATALOG):
                buy_btn = pygame.Rect(100, 160 + idx * 52, 340, 44)
                is_hov = buy_btn.collidepoint(mx, my)
                pygame.draw.rect(self.screen, (30, 50, 75) if is_hov else (20, 32, 48), buy_btn)
                pygame.draw.rect(self.screen, (0, 220, 255) if is_hov else (60, 100, 140), buy_btn, 1)

                name_l = sub_font.render(f"{sys_item['name']} - {sys_item['price']} Scrap", True, (240, 255, 255))
                desc_l = tiny_font.render(sys_item['desc'], True, (170, 200, 230))
                self.screen.blit(name_l, (buy_btn.x + 10, buy_btn.y + 5))
                self.screen.blit(desc_l, (buy_btn.x + 10, buy_btn.y + 24))

            hdr_sell_sys = sub_font.render("ZUSATZSYSTEME VERKAUFEN (50% Scrap Erstattung):", True, (255, 220, 100))
            self.screen.blit(hdr_sell_sys, (470, 138))

            empty_or_optional_rooms = [
                r for r in self.data.player.ship.rooms
                if r.name not in PROTECTED_CORE_SYSTEMS and r.name != "[Freier Raum-Slot]"
            ]

            if not empty_or_optional_rooms:
                self.screen.blit(tiny_font.render("Keine verkaufbaren Zusatzsysteme installiert.", True, (160, 180, 200)), (470, 165))
            else:
                for idx, r in enumerate(empty_or_optional_rooms):
                    sell_btn = pygame.Rect(470, 160 + idx * 52, 350, 44)
                    is_hov = sell_btn.collidepoint(mx, my)
                    pygame.draw.rect(self.screen, (80, 35, 35) if is_hov else (50, 24, 24), sell_btn)
                    pygame.draw.rect(self.screen, (255, 100, 100) if is_hov else (160, 60, 60), sell_btn, 1)

                    cat_info = next((item for item in SYSTEM_ROOM_CATALOG if item["name"] == r.name), None)
                    refund = (cat_info["price"] // 2) if cat_info else 25
                    r_lbl = sub_font.render(f"{r.name} verkaufen (+{refund} Scrap)", True, (255, 220, 220))
                    p_lbl = tiny_font.render(f"Max Power: {r.max_power} | Zustand: {int(r.health)}%", True, (220, 180, 180))
                    self.screen.blit(r_lbl, (sell_btn.x + 10, sell_btn.y + 5))
                    self.screen.blit(p_lbl, (sell_btn.x + 10, sell_btn.y + 24))

        # Shop verlassen Button (Gemeinsam unten)
        btn_leave = pygame.Rect(340, 495, 220, 40)
        self.draw_scifi_button(
            btn_leave,
            "Shop verlassen",
            is_hovered=btn_leave.collidepoint(mx, my),
            primary_color=(255, 80, 80),
        )

        # Modal 1: Layout-Umbau Modal Overlay
        is_swap_mode = getattr(shop_mgr, "layout_swap_mode", False) if shop_mgr else False
        first_r = getattr(shop_mgr, "layout_swap_first_room", None) if shop_mgr else None

        if is_swap_mode:
            overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 15, 25, 220))
            self.screen.blit(overlay, (0, 0))

            swap_type = getattr(shop_mgr, "layout_swap_type", "ROOMS")
            first_sel = getattr(shop_mgr, "layout_swap_first_selection", None)

            # Tab-Buttons rendern
            tab_rooms = pygame.Rect(200, 20, 190, 32)
            tab_weapons = pygame.Rect(410, 20, 190, 32)

            col_r_fill = (50, 70, 100) if swap_type == "ROOMS" else (25, 35, 50)
            col_r_bord = (255, 220, 100) if swap_type == "ROOMS" else (80, 120, 160)
            pygame.draw.rect(self.screen, col_r_fill, tab_rooms)
            pygame.draw.rect(self.screen, col_r_bord, tab_rooms, 2)
            lbl_tr = self.small_font.render("Räume tauschen", True, (255, 255, 255))
            self.screen.blit(lbl_tr, (tab_rooms.x + (tab_rooms.width - lbl_tr.get_width()) // 2, tab_rooms.y + 8))

            col_w_fill = (50, 70, 100) if swap_type == "WEAPONS" else (25, 35, 50)
            col_w_bord = (255, 220, 100) if swap_type == "WEAPONS" else (80, 120, 160)
            pygame.draw.rect(self.screen, col_w_fill, tab_weapons)
            pygame.draw.rect(self.screen, col_w_bord, tab_weapons, 2)
            lbl_tw = self.small_font.render("Waffenslots tauschen", True, (255, 255, 255))
            self.screen.blit(lbl_tw, (tab_weapons.x + (tab_weapons.width - lbl_tw.get_width()) // 2, tab_weapons.y + 8))

            if swap_type == "ROOMS":
                first_r_name = first_sel.name if (first_sel and hasattr(first_sel, "name")) else ""
                subtitle_txt = f"1. Raum: {first_r_name.upper()} | Klicke auf den 2. Raum zum Tauschen!" if first_r_name else "KLICKE AUF ZWEI RÄUME, UM DEREN SYSTEME ZU TAUSCHEN:"
            else:
                s1_num = f"H{first_sel+1}" if isinstance(first_sel, int) else ""
                subtitle_txt = f"1. Slot: {s1_num} | Klicke auf den 2. Waffenslot zum Tauschen!" if s1_num else "KLICKE AUF ZWEI WAFFENSLOTS, UM DEREN TYPEN ZU TAUSCHEN:"

            st_lbl = self.small_font.render(subtitle_txt, True, (100, 220, 255))
            self.screen.blit(st_lbl, (220, 58))

            if swap_type == "ROOMS":
                # Spielerschiff Räume zeichnen
                for r in self.data.player.ship.rooms:
                    is_first = (r == first_sel)
                    border_color = (255, 220, 0) if is_first else (100, 200, 255)
                    fill_color = (70, 70, 20) if is_first else (30, 45, 65)

                    pygame.draw.rect(self.screen, fill_color, r.rect)
                    pygame.draw.rect(self.screen, border_color, r.rect, 3 if is_first else 2)

                    lbl_r = self.small_font.render(r.name, True, (255, 255, 255))
                    self.screen.blit(lbl_r, (r.rect.x + 6, r.rect.y + 6))
            else:
                # Spielerschiff Räume abgedunkelt im Hintergrund
                for r in self.data.player.ship.rooms:
                    pygame.draw.rect(self.screen, (20, 30, 45), r.rect)
                    pygame.draw.rect(self.screen, (40, 60, 90), r.rect, 1)

                # Waffenslot-Karten zeichnen
                tiny_font = pygame.font.SysFont(None, 13)
                small_font = pygame.font.SysFont(None, 14, bold=True)
                for idx, slot in enumerate(getattr(self.data.player.ship, "weapon_slots", [])):
                    hx, hy = slot["pos"]
                    slot_rect = pygame.Rect(hx - 65, hy - 25, 130, 50)
                    is_first = (isinstance(first_sel, int) and first_sel == idx)

                    b_fill = (80, 75, 25) if is_first else (22, 35, 55)
                    b_bord = (255, 220, 0) if is_first else (100, 200, 255)

                    pygame.draw.rect(self.screen, b_fill, slot_rect)
                    pygame.draw.rect(self.screen, b_bord, slot_rect, 2)

                    allowed = slot.get("allowed_types")
                    allowed_str = ", ".join(allowed) if allowed else "ALLE"
                    w_name = self.data.player.weapons[idx].name if idx < len(self.data.player.weapons) else "[Leer]"

                    lbl_title = small_font.render(f"Slot H{idx+1}", True, (255, 220, 100) if is_first else (200, 240, 255))
                    lbl_type = tiny_font.render(f"Typ: {allowed_str}", True, (160, 220, 255))
                    lbl_weap = tiny_font.render(f"Waffe: {w_name}", True, (255, 255, 200))

                    self.screen.blit(lbl_title, (slot_rect.x + 6, slot_rect.y + 4))
                    self.screen.blit(lbl_type, (slot_rect.x + 6, slot_rect.y + 20))
                    self.screen.blit(lbl_weap, (slot_rect.x + 6, slot_rect.y + 34))

            cancel_btn = pygame.Rect(320, 490, 260, 40)
            pygame.draw.rect(self.screen, (70, 40, 40), cancel_btn)
            pygame.draw.rect(self.screen, (255, 120, 120), cancel_btn, 2)
            c_lbl = self.font.render("Umbau Abbrechen", True, (255, 200, 200))
            self.screen.blit(c_lbl, (cancel_btn.x + 40, cancel_btn.y + 10))
            return

        sel_item = getattr(shop_mgr, "selecting_slot_item", None) if shop_mgr else None
        if sel_item:
            overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 15, 25, 220))
            self.screen.blit(overlay, (0, 0))

            dialog = pygame.Rect(120, 90, 660, 390)
            pygame.draw.rect(self.screen, (25, 35, 55), dialog)
            pygame.draw.rect(self.screen, (100, 200, 255), dialog, 3)

            title = self.font.render(f"Wähle Slot für {sel_item['name']} ({sel_item['price']} Scrap):", True, (255, 220, 100))
            self.screen.blit(title, (dialog.x + 30, dialog.y + 20))

            for slot_i in range(max_slots):
                s_btn = pygame.Rect(150, 150 + slot_i * 65, 600, 52)
                pygame.draw.rect(self.screen, (40, 60, 85), s_btn)
                pygame.draw.rect(self.screen, COLOR_BORDER, s_btn, 2)

                s_info = slots[slot_i] if slot_i < len(slots) else {}
                al_types = s_info.get("allowed_types")
                al_str = ", ".join(al_types) if al_types else "Alle Typen"

                has_w = slot_i < len(self.data.player.weapons)
                w_obj = self.data.player.weapons[slot_i] if has_w else None

                if not has_w or w_obj is None:
                    status_str = "Einbauen (Slot Leer)"
                elif w_obj.w_type == sel_item.get("w_type"):
                    status_str = f"WAFFEN-FUSION (Upgrade MK {w_obj.level} -> MK {w_obj.level+1})"
                else:
                    status_str = f"ERSETZEN (Alte Waffe {w_obj.name} verkaufen)"

                txt1 = self.font.render(f"Slot {slot_i+1} [Erlaubt: {al_str}]: {status_str}", True, (220, 240, 255))
                self.screen.blit(txt1, (s_btn.x + 15, s_btn.y + 15))

            cancel_btn = pygame.Rect(320, 420, 240, 38)
            pygame.draw.rect(self.screen, (70, 40, 40), cancel_btn)
            pygame.draw.rect(self.screen, (255, 120, 120), cancel_btn, 2)
            c_lbl = self.font.render("Abbrechen", True, (255, 200, 200))
            self.screen.blit(c_lbl, (cancel_btn.x + 70, cancel_btn.y + 8))

    def draw_training(self):
        panel_rect = pygame.Rect(40, 30, 820, 540)
        pygame.draw.rect(self.screen, (20, 25, 40), panel_rect)
        pygame.draw.rect(self.screen, COLOR_TRAINING_NODE, panel_rect, 3)

        title_lbl = self.title_font.render("CREW-TRAININGSSATZ (20 Scrap / Skill)", True, (220, 180, 255))
        scrap_lbl = self.font.render(f"Dein Schrott: {self.data.player.scrap} Scrap", True, (255, 220, 100))
        self.screen.blit(title_lbl, (60, 45))
        self.screen.blit(scrap_lbl, (670, 52))

        tiny_font = pygame.font.SysFont(None, 15)

        skills = [
            ("repair", "Reparatur", "+25% Tempo"),
            ("combat", "Nahkampf", "+30% Schaden"),
            ("piloting", "Piloten", "+5% Evasion"),
            ("fitness", "Fitness", "+15 Max HP"),
        ]

        for c_idx, crew in enumerate(self.data.player.crew):
            card_y = 100 + c_idx * 95
            card_rect = pygame.Rect(55, card_y, 790, 85)
            pygame.draw.rect(self.screen, (30, 40, 60), card_rect)
            pygame.draw.rect(self.screen, COLOR_BORDER, card_rect, 1)

            # Crew-Icon & Details
            c_color = (100, 200, 255) if crew.species == "Engi" else ((200, 255, 100) if crew.species == "Mantis" else COLOR_CREW)
            pygame.draw.circle(self.screen, c_color, (card_rect.x + 30, card_rect.y + 30), 16)
            b_lbl = self.font.render(crew.species[0], True, (0, 0, 0))
            self.screen.blit(b_lbl, (card_rect.x + 24, card_rect.y + 18))

            name_txt = self.font.render(f"{crew.name} ({crew.species})", True, (240, 240, 255))
            hp_txt = tiny_font.render(f"HP: {int(crew.hp)}/{int(crew.max_hp)} | Trait: {crew.trait}", True, (180, 220, 240))
            self.screen.blit(name_txt, (card_rect.x + 60, card_rect.y + 12))
            self.screen.blit(hp_txt, (card_rect.x + 60, card_rect.y + 36))

            # Render 4 Skill Upgrade Cards
            for s_idx, (s_key, s_name, s_desc) in enumerate(skills):
                s_box = pygame.Rect(465 + s_idx * 98, card_y + 8, 92, 68)
                pygame.draw.rect(self.screen, (22, 30, 48), s_box)
                pygame.draw.rect(self.screen, (70, 90, 130), s_box, 1)

                cur_lvl = getattr(crew, f"skill_{s_key}", 0)
                lvl_str = f"Lvl {cur_lvl}/3" if cur_lvl < 3 else "[MAX]"

                lbl_sname = tiny_font.render(f"{s_name}", True, (220, 220, 255))
                lbl_sdesc = tiny_font.render(lvl_str, True, (160, 220, 255))
                self.screen.blit(lbl_sname, (s_box.x + 4, s_box.y + 4))
                self.screen.blit(lbl_sdesc, (s_box.x + 4, s_box.y + 18))

                upg_btn = pygame.Rect(s_box.x + 4, s_box.y + 36, 84, 26)
                b_col = (110, 50, 160) if cur_lvl < 3 else (50, 60, 70)
                pygame.draw.rect(self.screen, b_col, upg_btn)
                pygame.draw.rect(self.screen, (210, 150, 255) if cur_lvl < 3 else (100, 100, 100), upg_btn, 1)

                btn_txt_str = "Trainieren" if cur_lvl < 3 else "Max"
                upg_lbl = tiny_font.render(btn_txt_str, True, (255, 255, 255) if cur_lvl < 3 else (160, 160, 160))
                self.screen.blit(upg_lbl, (upg_btn.x + (upg_btn.width - upg_lbl.get_width()) // 2, upg_btn.y + 6))

        # Button zum Verlassen
        btn_leave = pygame.Rect(320, 510, 260, 42)
        pygame.draw.rect(self.screen, (60, 40, 70), btn_leave)
        pygame.draw.rect(self.screen, COLOR_TRAINING_NODE, btn_leave, 2)
        l_lbl = self.font.render("Station verlassen", True, (240, 200, 255))
        self.screen.blit(l_lbl, (btn_leave.x + (btn_leave.width - l_lbl.get_width()) // 2, btn_leave.y + 10))

    def draw_rooms(self):
        is_enemy_destroyed = (self.data.enemy.ship.hp <= 0) or getattr(self.data.combat, "combat_won", False)

        # 0. Schiffshüllen (Player & Enemy Hull Sprites)
        if "kestrel_hull" in self.assets and self.data.player.ship.rooms:
            p_rooms = self.data.player.ship.rooms
            min_x = min(r.rect.left for r in p_rooms) - 25
            min_y = min(r.rect.top for r in p_rooms) - 25
            self.screen.blit(self.assets["kestrel_hull"], (min_x, min_y))

        if not is_enemy_destroyed and "enemy_scout" in self.assets and self.data.enemy.ship.rooms:
            e_rooms = self.data.enemy.ship.rooms
            min_x = min(r.rect.left for r in e_rooms) - 25
            min_y = min(r.rect.top for r in e_rooms) - 25
            self.screen.blit(self.assets["enemy_scout"], (min_x, min_y))

        # 1. Reaktor zeichnen (links am Rand)
        self.data.player.reactor.draw(self.screen, 15, 45)

        # Kompakte Infoboxen OBERHALB der Schiffe
        small_font = pygame.font.SysFont(None, 17, bold=True)

        p_box = pygame.Rect(10, 34, 225, 22)
        p_surf = pygame.Surface((p_box.width, p_box.height), pygame.SRCALPHA)
        p_surf.fill((14, 25, 42, 210))
        self.screen.blit(p_surf, (p_box.x, p_box.y))
        pygame.draw.rect(self.screen, (0, 200, 255), p_box, 1)

        if hasattr(self.data, "combat_manager") and hasattr(self.game.combat_manager, "get_player_evasion"):
            evade_val = int(self.game.combat_manager.get_player_evasion() * 100)
        else:
            evade_val = int(self.data.player.ship.rooms[2].current_power * 0.20 * 100) if len(self.data.player.ship.rooms) > 2 else 10
        p_lbl = small_font.render(f"Spieler Hülle: {self.data.player.ship.hp}/{self.data.player.ship.max_hp} HP  |  Ausw: {evade_val}%", True, (130, 240, 170))
        self.screen.blit(p_lbl, (p_box.x + 8, p_box.y + 4))

        if not is_enemy_destroyed:
            e_box = pygame.Rect(520, 34, 225, 22)
            e_surf = pygame.Surface((e_box.width, e_box.height), pygame.SRCALPHA)
            e_surf.fill((35, 18, 25, 210))
            self.screen.blit(e_surf, (e_box.x, e_box.y))
            pygame.draw.rect(self.screen, (255, 90, 90), e_box, 1)

            e_name = getattr(self.data.enemy.ship, "name", "Gegner")
            e_disp = e_name if len(e_name) <= 12 else e_name[:11] + "."
            e_lbl = small_font.render(f"{e_disp}: {self.data.enemy.ship.hp}/{self.data.enemy.ship.max_hp} HP", True, (255, 140, 140))
            self.screen.blit(e_lbl, (e_box.x + 8, e_box.y + 4))

        # Tarnungs-Effekt (Stealth Shimmer) auf eigenem Schiff
        cloak_active = getattr(self.data.combat, "cloak_active_timer", 0.0) > 0.0
        if cloak_active:
            s_overlay = pygame.Surface((380, 240), pygame.SRCALPHA)
            s_overlay.fill((0, 220, 255, 35))
            self.screen.blit(s_overlay, (50, 95))

        # 2. Räume & Türen zeichnen
        manned_font = pygame.font.SysFont(None, 14, bold=True)
        for r in self.data.player.ship.rooms:
            r.draw(self.screen)
            m_count = len([c for c in self.data.player.crew if c.current_room == r])
            if m_count > 0 and r.name in ("Waffen", "Schild", "Brücke", "Maschinen", "Medbay", "Drohnen-Kontrolle"):
                badge_str = "[M]" if m_count == 1 else "[MM]"
                lbl_m = manned_font.render(badge_str, True, (255, 220, 100))
                self.screen.blit(lbl_m, (r.rect.left + 3, r.rect.top + 3))

        # Sensor-Stufen Prüfung
        sens_room = next((r for r in self.data.player.ship.rooms if r.name == "Sensoren"), None)
        sensor_power = sens_room.current_power if sens_room else 1

        if not is_enemy_destroyed:
            for r in self.data.enemy.ship.rooms:
                r.draw(self.screen)
                if sensor_power == 0:
                    # Fog of War Overlay über dem Gegnerschiff
                    pygame.draw.rect(self.screen, (20, 25, 35), r.rect)
                    pygame.draw.rect(self.screen, (40, 50, 70), r.rect, 2)
                    f_font = pygame.font.SysFont(None, 13)
                    lbl = f_font.render("NEBEL", True, (100, 120, 150))
                    self.screen.blit(lbl, (r.rect.centerx - lbl.get_width() // 2, r.rect.centery - lbl.get_height() // 2))

        door_room = next((r for r in self.data.player.ship.rooms if r.name == "Türen"), None)
        door_level = door_room.current_power if door_room else 1
        self.data.player.ship.draw_doors(self.screen, door_level=door_level)
        if not is_enemy_destroyed:
            self.data.enemy.ship.draw_doors(self.screen)

        # Hardpoint Waffenslots auf den Schiffen zeichnen
        small_font = pygame.font.SysFont(None, 14)
        for s_idx, slot in enumerate(getattr(self.data.player.ship, "weapon_slots", [])):
            hx, hy = slot["pos"]
            pygame.draw.circle(self.screen, (20, 30, 45), (hx, hy), 7)
            pygame.draw.circle(self.screen, (100, 220, 255), (hx, hy), 7, 2)
            pygame.draw.circle(self.screen, (255, 200, 100), (hx, hy), 2)
            lbl = small_font.render(f"H{s_idx+1}", True, (180, 230, 255))
            self.screen.blit(lbl, (hx - 6, hy - 16))

        if not is_enemy_destroyed:
            for s_idx, slot in enumerate(getattr(self.data.enemy.ship, "weapon_slots", [])):
                hx, hy = slot["pos"]
                pygame.draw.circle(self.screen, (45, 20, 20), (hx, hy), 7)
                pygame.draw.circle(self.screen, (255, 100, 100), (hx, hy), 7, 2)
                pygame.draw.circle(self.screen, (255, 200, 100), (hx, hy), 2)

        # 3. Crew zeichnen (wenn Sensor-Stufe >= 1 für Gegnerschiff)
        for c in self.data.player.crew:
            if c.is_boarding and sensor_power == 0:
                continue
            c.draw(self.screen)

        if sensor_power >= 1:
            for c in getattr(self.game.combat_manager, "enemy_crew", []):
                c.draw(self.screen)

        # 4. Drohnen im Raum & Orbit zeichnen
        import math
        p_rooms = self.data.player.ship.rooms
        p_cx = (min(r.rect.left for r in p_rooms) + max(r.rect.right for r in p_rooms)) // 2 if p_rooms else 220
        p_cy = (min(r.rect.top for r in p_rooms) + max(r.rect.bottom for r in p_rooms)) // 2 if p_rooms else 245

        e_rooms = self.data.enemy.ship.rooms
        e_cx = (min(r.rect.left for r in e_rooms) + max(r.rect.right for r in e_rooms)) // 2 if e_rooms else 710
        e_cy = (min(r.rect.top for r in e_rooms) + max(r.rect.bottom for r in e_rooms)) // 2 if e_rooms else 245

        if getattr(self.data.combat, "combat_drone_active", False):
            ang = getattr(self.data.combat, "drone_orbit_angle", 0.0)
            d_x = int(e_cx + math.cos(ang) * 160)
            d_y = int(e_cy + math.sin(ang) * 110)
            pygame.draw.circle(self.screen, (255, 100, 50), (d_x, d_y), 9)
            pygame.draw.circle(self.screen, (255, 255, 255), (d_x, d_y), 9, 2)
            d_lbl = small_font.render("KAMPFDROHNE", True, (255, 160, 100))
            self.screen.blit(d_lbl, (d_x - d_lbl.get_width() // 2, d_y - 18))

        if getattr(self.data.combat, "repair_drone_active", False):
            rx, ry = getattr(self.data.combat, "repair_drone_pos", (float(p_cx), float(p_cy)))
            pygame.draw.rect(self.screen, (160, 190, 220), (int(rx) - 10, int(ry) - 10, 20, 20))
            pygame.draw.rect(self.screen, (50, 220, 100), (int(rx) - 10, int(ry) - 10, 20, 20), 2)
            r_lbl = small_font.render("REP-DROHNE", True, (100, 255, 100))
            self.screen.blit(r_lbl, (int(rx) - r_lbl.get_width() // 2, int(ry) + 12))

        if getattr(self.data.combat, "defense_drone_active", False):
            ang = getattr(self.data.combat, "drone_orbit_angle", 0.0)
            d_x = int(p_cx + math.cos(ang) * 130)
            d_y = int(p_cy + math.sin(ang) * 100)
            pygame.draw.circle(self.screen, (0, 220, 255), (d_x, d_y), 8)
            pygame.draw.circle(self.screen, (255, 255, 255), (d_x, d_y), 8, 2)
            def_lbl = small_font.render("VERT-DROHNE", True, (100, 230, 255))
            self.screen.blit(def_lbl, (d_x - def_lbl.get_width() // 2, d_y - 17))

            # Point defense laser beam
            d_beam = getattr(self.data.combat, "defense_laser_beam", None)
            if d_beam:
                pygame.draw.line(self.screen, (0, 255, 255), d_beam[0], d_beam[1], 3)
                pygame.draw.circle(self.screen, (255, 255, 255), d_beam[1], 6)

        if getattr(self.data.combat, "shield_charger_active", False):
            s_room = self.data.player.ship.rooms[0]
            cx, cy = s_room.rect.centerx - 25, s_room.rect.centery - 25
            pygame.draw.circle(self.screen, (255, 215, 0), (cx, cy), 8)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 8, 2)
            sc_lbl = small_font.render("SCHILD-DROHNE", True, (255, 230, 100))
            self.screen.blit(sc_lbl, (cx - sc_lbl.get_width() // 2, cy - 16))

        if getattr(self.data.combat, "anti_personnel_active", False):
            ap_x, ap_y = getattr(self.data.combat, "anti_personnel_pos", (220.0, 245.0))
            pygame.draw.rect(self.screen, (180, 50, 50), (int(ap_x) - 9, int(ap_y) - 9, 18, 18))
            pygame.draw.rect(self.screen, (255, 200, 50), (int(ap_x) - 9, int(ap_y) - 9, 18, 18), 2)
            ap_lbl = small_font.render("ANTI-PERS", True, (255, 140, 100))
            self.screen.blit(ap_lbl, (int(ap_x) - ap_lbl.get_width() // 2, int(ap_y) + 11))

        # Zoltan Super-Schild Aura (Phase 3 Boss)
        zoltan_hp = getattr(self.data.combat, "zoltan_shield_hp", 0)
        if zoltan_hp > 0:
            pygame.draw.ellipse(self.screen, (100, 255, 120), (530, 80, 350, 220), 4)
            z_font = pygame.font.SysFont(None, 14, bold=True)
            z_lbl = z_font.render(f"ZOLTAN SUPER-SCHILD: {zoltan_hp} HP", True, (120, 255, 150))
            self.screen.blit(z_lbl, (705 - z_lbl.get_width() // 2, 65))

        # 5. Sensor-Level 2 & 3: Gegner Waffendetails & Raum-Energie
        if sensor_power >= 2:
            e_w = self.data.enemy.weapon
            w_ratio = min(1.0, e_w.current_charge / e_w.charge_time)
            pygame.draw.rect(self.screen, (40, 30, 30), (550, 180, 150, 14))
            pygame.draw.rect(self.screen, (255, 140, 50), (550, 180, int(150 * w_ratio), 14))
            pygame.draw.rect(self.screen, (200, 100, 100), (550, 180, 150, 14), 1)
            w_lbl = small_font.render(f"Gegner-Waffe ({e_w.name}): {int(w_ratio*100)}%", True, (255, 220, 180))
            self.screen.blit(w_lbl, (550, 166))

    def draw_shields(self):
        p_rooms = self.data.player.ship.rooms
        p_cx = (min(r.rect.left for r in p_rooms) + max(r.rect.right for r in p_rooms)) // 2 if p_rooms else 220
        p_cy = (min(r.rect.top for r in p_rooms) + max(r.rect.bottom for r in p_rooms)) // 2 if p_rooms else 245

        self.data.player.shield.draw_bubble(self.screen, (p_cx, p_cy), 170)

        is_enemy_destroyed = (self.data.enemy.ship.hp <= 0) or getattr(self.data.combat, "combat_won", False)
        if not is_enemy_destroyed:
            e_rooms = self.data.enemy.ship.rooms
            e_cx = (min(r.rect.left for r in e_rooms) + max(r.rect.right for r in e_rooms)) // 2 if e_rooms else 710
            e_cy = (min(r.rect.top for r in e_rooms) + max(r.rect.bottom for r in e_rooms)) // 2 if e_rooms else 245
            self.data.enemy.shield.draw_bubble(self.screen, (e_cx, e_cy), 150)

    def draw_projectiles(self):
        for p in self.data.player.projectiles:
            p.draw(self.screen)

    def _logical_mouse_pos(self) -> tuple[int, int]:
        raw_mx, raw_my = pygame.mouse.get_pos()
        game_ref = getattr(self, "game", None)
        if game_ref and hasattr(game_ref, "screen_to_logical"):
            return game_ref.screen_to_logical(raw_mx, raw_my)
        return raw_mx, raw_my

    def draw_weapons(self):
        is_enemy_destroyed = (self.data.enemy.ship.hp <= 0) or getattr(self.data.combat, "combat_won", False)
        if not is_enemy_destroyed:
            # 1. Dauerhafte Schusslinien (Weapon Targets)
            for idx, (_, start_p, end_p) in self.data.combat.weapon_targets.items():
                color_line = WEAPON_LINE_COLORS[idx % len(WEAPON_LINE_COLORS)]
                pygame.draw.line(self.screen, color_line, start_p, end_p, 2)
                pygame.draw.circle(self.screen, color_line, end_p, 7, 2)
                w_badge = self.font.render(f"W{idx+1}", True, color_line)
                self.screen.blit(w_badge, (end_p[0] + 10, end_p[1] - 8))

        # 2. Zielen-Linie (beim aktiven Zielen mit Maus)
        if self.data.combat.is_targeting:
            mx, my = self._logical_mouse_pos()
            t_idx = self.data.combat.target_weapon_idx if self.data.combat.target_weapon_idx is not None else 0
            color_line = WEAPON_LINE_COLORS[t_idx % len(WEAPON_LINE_COLORS)]
            start = self.data.combat.start_pos

            # Reichweiten-Kreis & Out-of-Range-Anzeige
            weapon = None
            if t_idx < len(self.data.player.weapons):
                weapon = self.data.player.weapons[t_idx]
            if weapon and weapon.max_range is not None:
                # Reichweiten-Kreis zeichnen
                range_surf = pygame.Surface((int(weapon.max_range * 2) + 4, int(weapon.max_range * 2) + 4), pygame.SRCALPHA)
                pygame.draw.circle(range_surf, (*color_line, 40), (int(weapon.max_range) + 2, int(weapon.max_range) + 2), int(weapon.max_range), 2)
                self.screen.blit(range_surf, (int(start[0] - weapon.max_range - 2), int(start[1] - weapon.max_range - 2)))

                dist_to_mouse = math.hypot(mx - start[0], my - start[1])
                if dist_to_mouse > weapon.max_range:
                    # Rote Ziel-Linie und Warnung
                    pygame.draw.line(self.screen, (255, 60, 60), start, (mx, my), 2)
                    pygame.draw.circle(self.screen, (255, 60, 60), (mx, my), 7, 2)
                    oor_lbl = self.font.render("AUSSER REICHWEITE", True, (255, 60, 60))
                    self.screen.blit(oor_lbl, (mx + 10, my - 20))
                else:
                    pygame.draw.line(self.screen, color_line, start, (mx, my), 2)
                    pygame.draw.circle(self.screen, color_line, (mx, my), 7, 2)
            else:
                pygame.draw.line(self.screen, color_line, start, (mx, my), 2)
                pygame.draw.circle(self.screen, color_line, (mx, my), 7, 2)
            w_badge = self.font.render(f"W{t_idx+1}", True, color_line)
            self.screen.blit(w_badge, (mx + 10, my - 8))

        # 3. Waffen-UI-Bars (Unten Links)
        weapon_ui_y = 465
        self.screen.blit(self.font.render("Waffensysteme:", True, (200, 220, 255)), (25, weapon_ui_y))
        small_font = pygame.font.SysFont(None, 18)
        for i, w in enumerate(self.data.player.weapons):
            bar_x, bar_y = 25 + i * 125, weapon_ui_y + 35
            charge_ratio = w.current_charge / w.charge_time
            pygame.draw.rect(self.screen, (30, 35, 45), (bar_x, bar_y, 115, 16))
            bar_color = COLOR_POWER_ACTIVE if w.is_ready() else COLOR_WEAPON_CHARGE
            pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, int(115 * charge_ratio), 16))
            pygame.draw.rect(self.screen, COLOR_BORDER, (bar_x, bar_y, 115, 16), 1)

            w_color = WEAPON_LINE_COLORS[i % len(WEAPON_LINE_COLORS)]
            target_indicator = f" [W{i+1}]" if i in self.data.combat.weapon_targets else ""
            lbl_color = w_color if i in self.data.combat.weapon_targets else (200, 220, 255)
            disp_name = w.name if len(w.name) <= 14 else w.name[:13] + "."
            lbl = small_font.render(f"{disp_name}{target_indicator}", True, lbl_color)
            self.screen.blit(lbl, (bar_x, bar_y - 18))

            # Reichweiten-Anzeige unter der Ladeleiste
            if w.max_range is not None:
                range_lbl = small_font.render(f"R:{int(w.max_range)}", True, (180, 180, 200))
                self.screen.blit(range_lbl, (bar_x + 75, bar_y + 1))

        # 4. Untere Aktions-Buttons (Sci-Fi Glassmorphism Style)
        mx, my = self._logical_mouse_pos()

        tp_cd = getattr(self.data.combat, "teleport_cooldown", 0.0)
        is_tp_target = getattr(self.data.combat, "is_teleport_targeting", False)
        has_boarders = any(getattr(c, "is_boarding", False) for c in self.data.player.crew)
        tp_label = "ZIEL WÄHLEN..." if is_tp_target else ("ENTERN [BEAM]" if tp_cd <= 0 else f"ENTERN ({int(tp_cd)}s)")

        cloak_room = next((r for r in self.data.player.ship.rooms if r.name == "Tarnung"), None)
        cloak_active = getattr(self.data.combat, "cloak_active_timer", 0.0)
        cloak_cd = getattr(self.data.combat, "cloak_cooldown", 0.0)
        cloak_ready = cloak_room and cloak_room.current_power > 0 and cloak_cd <= 0.0 and cloak_active <= 0.0
        cloak_lbl = f"TARNUNG ({int(cloak_active)}s)" if cloak_active > 0 else ("TARNUNG [CLOAK]" if cloak_ready else f"TARNUNG ({int(cloak_cd)}s)")

        drone_room = next((r for r in self.data.player.ship.rooms if r.name == "Drohnen-Kontrolle"), None)
        drone_power = drone_room.current_power if drone_room else 0
        c_active = getattr(self.data.combat, "combat_drone_active", False)
        r_active = getattr(self.data.combat, "repair_drone_active", False)

        c_drone_lbl = "KAMPFDROHNE [1E]" if not c_active else "KAMPFDROHNE [AKTIV]"
        r_drone_lbl = "REP-DROHNE [2E]" if not r_active else "REP-DROHNE [AKTIV]"

        self.draw_scifi_button(
            self.btn_repair_drone,
            r_drone_lbl,
            is_active=r_active,
            is_hovered=self.btn_repair_drone.collidepoint(mx, my),
            primary_color=(0, 220, 150) if r_active else (0, 200, 255),
            enabled=(drone_power >= 2 or r_active),
        )
        self.draw_scifi_button(
            self.btn_combat_drone,
            c_drone_lbl,
            is_active=c_active,
            is_hovered=self.btn_combat_drone.collidepoint(mx, my),
            primary_color=(255, 140, 50),
            enabled=(drone_power >= 1 or c_active),
        )
        self.draw_scifi_button(
            self.btn_cloak,
            cloak_lbl,
            is_active=(cloak_active > 0),
            is_hovered=self.btn_cloak.collidepoint(mx, my),
            primary_color=(180, 120, 255),
            enabled=(cloak_ready or cloak_active > 0),
        )

        combat_won = getattr(self.data.combat, "combat_won", False)
        ftl_timer = getattr(self.data.combat, "ftl_charge_timer", 0.0)
        ftl_ready = getattr(self.data.combat, "ftl_ready", False) or combat_won
        ftl_pct = int((ftl_timer / 30.0) * 100)
        if combat_won:
            ftl_lbl = "KARTENANSICHT"
        elif ftl_ready:
            ftl_lbl = "FLIEHEN [FTL BEREIT]"
        else:
            ftl_lbl = f"FTL LÄDT ({ftl_pct}%)"

        self.draw_scifi_button(
            self.btn_ftl,
            ftl_lbl,
            is_active=ftl_ready,
            is_hovered=self.btn_ftl.collidepoint(mx, my),
            primary_color=(50, 220, 100) if ftl_ready else (140, 160, 180),
            enabled=ftl_ready,
        )

        self.draw_scifi_button(
            self.btn_recall,
            "ZURÜCKBEAMEN",
            is_hovered=self.btn_recall.collidepoint(mx, my),
            primary_color=(240, 120, 50),
            enabled=has_boarders,
        )
        self.draw_scifi_button(
            self.btn_teleport,
            tp_label,
            is_hovered=self.btn_teleport.collidepoint(mx, my),
            primary_color=(0, 220, 255),
            enabled=(tp_cd <= 0),
        )
        self.draw_scifi_button(
            self.btn_autofire,
            f"AUTOFIRE: {'AN' if self.data.combat.autofire_enabled else 'AUS'}",
            is_hovered=self.btn_autofire.collidepoint(mx, my),
            primary_color=(0, 230, 140) if self.data.combat.autofire_enabled else (120, 140, 170),
        )

        # 5. Augmentations Badges
        augments = getattr(self.data.player, "augments", [])
        if augments:
            small_font = pygame.font.SysFont(None, 14, bold=True)
            for a_idx, aug_name in enumerate(augments):
                a_rect = pygame.Rect(25 + a_idx * 130, 520, 120, 24)
                pygame.draw.rect(self.screen, (30, 45, 65), a_rect)
                pygame.draw.rect(self.screen, (100, 200, 255), a_rect, 1)
                a_lbl = small_font.render(f"AUG: {aug_name[:12]}", True, (160, 230, 255))
                self.screen.blit(a_lbl, (a_rect.centerx - a_lbl.get_width() // 2, a_rect.centery - a_lbl.get_height() // 2))

    def draw_messages(self):
        # Boss Phase HUD Banner
        if "Flaggschiff" in getattr(self.data.enemy.ship, "name", ""):
            b_phase = getattr(self.data.combat, "boss_phase", 1)
            b_lbl = self.font.render(f"SEKTOR 5 FLAGGSCHIFF - PHASE {b_phase}/3", True, (255, 80, 80))
            self.screen.blit(b_lbl, (SCREEN_WIDTH // 2 - b_lbl.get_width() // 2, 40))

        # Umweltgefahren Banner
        current_node = self.data.world.star_map.current_node
        hazard = getattr(current_node, "hazard_type", "NONE") if current_node else "NONE"
        if hazard == "SOLAR_FLARE":
            sf_timer = getattr(self.data.combat, "solar_flare_timer", 20.0)
            h_lbl = self.font.render(f"SONNEN-ERUPTION IN: {int(sf_timer)}s", True, (255, 160, 50))
            self.screen.blit(h_lbl, (SCREEN_WIDTH // 2 - h_lbl.get_width() // 2, 75))
        elif hazard == "ASTEROID_FIELD":
            h_lbl = self.font.render("UMWELTGEFAHR: ASTEROIDENFELD", True, (180, 200, 240))
            self.screen.blit(h_lbl, (SCREEN_WIDTH // 2 - h_lbl.get_width() // 2, 75))
        elif hazard == "NEBULA_ION_STORM":
            h_lbl = self.font.render("UMWELTGEFAHR: NEBEL-ION-STURM (-50% REAKTOR-ENERGIE)", True, (0, 220, 255))
            self.screen.blit(h_lbl, (SCREEN_WIDTH // 2 - h_lbl.get_width() // 2, 75))
        elif hazard == "PULSAR":
            pulsar_t = getattr(self.data.combat, "pulsar_timer", 15.0)
            h_lbl = self.font.render(f"PULSAR-STRAHLUNG IN: {int(pulsar_t)}s", True, (255, 230, 80))
            self.screen.blit(h_lbl, (SCREEN_WIDTH // 2 - h_lbl.get_width() // 2, 75))

        # Temporäre Kampfnachrichten (Unten über der Waffenleiste)
        if self.data.combat.msg_timer > 0.0:
            msg_txt = self.font.render(self.data.combat.msg, True, COLOR_SELECTED)
            msg_box = pygame.Rect(SCREEN_WIDTH // 2 - msg_txt.get_width() // 2 - 10, 438, msg_txt.get_width() + 20, 24)
            pygame.draw.rect(self.screen, (15, 25, 40), msg_box)
            pygame.draw.rect(self.screen, COLOR_SELECTED, msg_box, 1)
            self.screen.blit(msg_txt, (msg_box.x + 10, msg_box.y + 4))

    def draw_pause_menu(self):
        overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 200))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, (25, 35, 50), (250, 90, 400, 420))
        pygame.draw.rect(self.screen, (100, 200, 255), (250, 90, 400, 420), 3)

        title_font = pygame.font.SysFont(None, 36, bold=True)
        title_txt = title_font.render("--- SPIEL PAUSIERT ---", True, (255, 255, 100))
        self.screen.blit(title_txt, (LOGICAL_WIDTH // 2 - title_txt.get_width() // 2, 110))

        buttons = [
            (self.btn_pause_resume, "Weiter (Spiel fortsetzen)", (50, 120, 70), (100, 255, 100)),
            (self.btn_pause_save, "Spiel Speichern (S)", (40, 60, 90), COLOR_BORDER),
            (self.btn_pause_load, "Spiel Laden (L)", (40, 60, 90), COLOR_BORDER),
            (self.btn_pause_options, "Optionen & Einstellungen", (60, 75, 100), (120, 160, 220)),
            (self.btn_pause_main_menu, "Zurück zum Hauptmenü", (80, 40, 40), (255, 100, 100)),
        ]

        for btn, text, bg_col, border_col in buttons:
            pygame.draw.rect(self.screen, bg_col, btn)
            pygame.draw.rect(self.screen, border_col, btn, 2)
            txt_surf = self.font.render(text, True, (240, 240, 240))
            self.screen.blit(txt_surf, (btn.x + (btn.width - txt_surf.get_width()) // 2, btn.y + 11))
            
    def is_any_modal_open(self) -> bool:
        shop_mgr = getattr(self.game, "shop_manager", None) or getattr(self.data, "shop_manager", None)
        is_shop_modal = (
            self.data.current_state == STATE_SHOP
            and shop_mgr is not None
            and (getattr(shop_mgr, "layout_swap_mode", False) or getattr(shop_mgr, "selecting_slot_item", None) is not None)
        )
        return (
            getattr(self.data, "show_pause_menu", False)
            or getattr(self.data, "show_slot_modal", False)
            or getattr(self.data, "show_help_overlay", False)
            or is_shop_modal
        )

    def draw_scifi_button(
        self,
        rect: pygame.Rect,
        text: str,
        is_active: bool = False,
        is_hovered: bool = False,
        primary_color: tuple[int, int, int] = (0, 200, 255),
        enabled: bool = True,
    ):
        if self.is_any_modal_open():
            is_hovered = False

        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        if not enabled:
            bg_col = (20, 25, 35, 180)
            border_col = (60, 70, 85)
            text_col = (120, 130, 145)
        elif is_hovered or is_active:
            bg_col = (primary_color[0] // 3, primary_color[1] // 3 + 20, primary_color[2] // 3 + 40, 220)
            border_col = (min(255, primary_color[0] + 50), min(255, primary_color[1] + 50), min(255, primary_color[2] + 50))
            text_col = (255, 255, 255)
        else:
            bg_col = (18, 28, 45, 190)
            border_col = primary_color
            text_col = (220, 240, 255)

        s.fill(bg_col)
        self.screen.blit(s, (rect.x, rect.y))

        b_width = 3 if (is_hovered or is_active) else 2
        pygame.draw.rect(self.screen, border_col, rect, b_width)

        if enabled:
            hl_color = (255, 255, 255, 100) if is_hovered else (border_col[0], border_col[1], border_col[2], 60)
            hl_surf = pygame.Surface((rect.width - 4, 2), pygame.SRCALPHA)
            hl_surf.fill(hl_color)
            self.screen.blit(hl_surf, (rect.x + 2, rect.y + 2))

        btn_font = pygame.font.SysFont(None, 22, bold=True)
        txt_surf = btn_font.render(text, True, text_col)
        self.screen.blit(
            txt_surf,
            (rect.x + (rect.width - txt_surf.get_width()) // 2, rect.y + (rect.height - txt_surf.get_height()) // 2),
        )

    def draw_main_menu(self):
        if "main_menu_bg" in self.assets:
            self.screen.blit(self.assets["main_menu_bg"], (0, 0))
        else:
            self.screen.fill((10, 15, 25))

        mx, my = self._logical_mouse_pos()

        # Header Title Banner
        banner_rect = pygame.Rect(LOGICAL_WIDTH // 2 - 270, 20, 540, 52)
        b_surf = pygame.Surface((banner_rect.width, banner_rect.height), pygame.SRCALPHA)
        b_surf.fill((12, 20, 35, 210))
        self.screen.blit(b_surf, (banner_rect.x, banner_rect.y))
        pygame.draw.rect(self.screen, (0, 200, 255), banner_rect, 2)

        title_font = pygame.font.SysFont(None, 36, bold=True)
        title_txt = title_font.render("FTL KLON: HANGAR & RAUMSCHIFFE", True, (240, 245, 255))
        self.screen.blit(
            title_txt, (banner_rect.x + (banner_rect.width - title_txt.get_width()) // 2, banner_rect.y + 12)
        )

        # 8 Schiffskarten in 2x4 Raster
        from classes.ShipModel import SHIP_BLUEPRINTS, SHIP_STARTING_SPECS, PLAYER_SHIP
        from managers.save_manager import SaveManager

        selected_name = getattr(self.data.player.ship, "name", "Kestrel")
        unlocked = getattr(self.data.player, "unlocked_ships", ["Kestrel"])

        col_x = [40, 250, 460, 670]
        row_y = [82, 226]
        ship_list = list(SHIP_BLUEPRINTS.items())

        hovered_ship_tuple = None

        for idx, (name, ship_obj) in enumerate(ship_list):
            r_idx = idx // 4
            c_idx = idx % 4
            if r_idx >= 2:
                break

            btn = pygame.Rect(col_x[c_idx], row_y[r_idx], 195, 138)
            is_sel = (name == selected_name)
            is_unlocked = (name in unlocked)
            is_hov = btn.collidepoint(mx, my)

            if is_hov:
                hovered_ship_tuple = (name, ship_obj)

            c_surf = pygame.Surface((btn.width, btn.height), pygame.SRCALPHA)
            if is_sel:
                c_surf.fill((25, 48, 75, 230))
                border_col = (0, 230, 180)
            elif is_hov:
                c_surf.fill((20, 38, 58, 210))
                border_col = (100, 200, 255)
            else:
                c_surf.fill((14, 22, 36, 190))
                border_col = (55, 75, 105)

            self.screen.blit(c_surf, (btn.x, btn.y))
            pygame.draw.rect(self.screen, border_col, btn, 3 if is_sel else (2 if is_hov else 1))

            name_disp = name if len(name) <= 15 else name[:14] + "."
            name_txt = self.font.render(name_disp, True, (255, 255, 255) if is_sel else (210, 220, 240))
            self.screen.blit(name_txt, (btn.x + 8, btn.y + 6))

            pygame.draw.line(
                self.screen, border_col, (btn.x + 6, btn.y + 28), (btn.x + btn.width - 6, btn.y + 28), 1
            )

            stat_font = pygame.font.SysFont(None, 16)
            stats_str = f"HP: {ship_obj.hp}  |  Waffen: {ship_obj.max_weapons}  |  Crew: {ship_obj.max_crew}"
            stats_txt = stat_font.render(stats_str, True, (140, 220, 240))
            self.screen.blit(stats_txt, (btn.x + 8, btn.y + 32))

            # Raum-Vorschau mit einheitlicher taktischer Stahl-Optik
            rooms_count = len(ship_obj.rooms)
            for r in range(min(rooms_count, 6)):
                rx = btn.x + 8 + r * 29
                ry = btn.y + 54
                r_name = ship_obj.rooms[r].name
                r_initial = r_name[0].upper()

                r_border = (0, 220, 255) if is_sel else (70, 105, 145)
                r_txt_col = (255, 255, 255) if is_sel else (170, 205, 235)

                pygame.draw.rect(self.screen, (20, 32, 48), (rx, ry, 25, 25))
                pygame.draw.rect(self.screen, r_border, (rx, ry, 25, 25), 1)
                init_lbl = stat_font.render(r_initial, True, r_txt_col)
                self.screen.blit(init_lbl, (rx + 8, ry + 5))

            sel_btn_rect = pygame.Rect(btn.x + 8, btn.y + 92, btn.width - 16, 36)
            if is_sel:
                self.draw_scifi_button(sel_btn_rect, "GEWÄHLT", is_active=True, primary_color=(0, 230, 140))
            elif is_unlocked:
                self.draw_scifi_button(sel_btn_rect, "WÄHLEN", is_hovered=is_hov, primary_color=(0, 180, 255))
            else:
                self.draw_scifi_button(sel_btn_rect, "GESPERRT", enabled=False)

        # -------------------------------------------------------------
        # SCHIFFS-INSPEKTOR PANEL (Taktische Sci-Fi Übersicht)
        # -------------------------------------------------------------
        inspector_rect = pygame.Rect(40, 372, 825, 148)
        pygame.draw.rect(self.screen, (16, 24, 38), inspector_rect)
        pygame.draw.rect(self.screen, (0, 200, 255), inspector_rect, 2)

        inspect_name, inspect_ship = hovered_ship_tuple if hovered_ship_tuple else (selected_name, SHIP_BLUEPRINTS.get(selected_name, PLAYER_SHIP))
        specs = SHIP_STARTING_SPECS.get(inspect_name, SHIP_STARTING_SPECS["Kestrel"])

        hdr_font = pygame.font.SysFont(None, 20, bold=True)
        body_font = pygame.font.SysFont(None, 16)
        small_font = pygame.font.SysFont(None, 14)

        insp_header = hdr_font.render(f"--- SCHIFFS-INSPEKTOR: {inspect_name.upper()} ---", True, (100, 220, 255))
        self.screen.blit(insp_header, (inspector_rect.x + 15, inspector_rect.y + 10))

        # Zeile 1: Crew & Waffen
        line1_str = f"BESATZUNG: {specs['crew_summary']}   |   START-WAFFEN: {specs['weapons_summary']}"
        self.screen.blit(body_font.render(line1_str, True, (255, 220, 100)), (inspector_rect.x + 15, inspector_rect.y + 32))

        # Zeile 2: Beschreibung
        self.screen.blit(body_font.render(f"DETAILS: {specs['desc']}", True, (200, 220, 240)), (inspector_rect.x + 15, inspector_rect.y + 54))

        # Zeile 3: Raum-Layout & Systeme
        rooms_str = ", ".join([r.name for r in inspect_ship.rooms])
        sys_str = f"SYSTEME ({len(inspect_ship.rooms)}): {rooms_str}"
        sys_lbl = small_font.render(sys_str, True, (160, 210, 245))
        self.screen.blit(sys_lbl, (inspector_rect.x + 15, inspector_rect.y + 76))

        # Zeile 4: Waffenslots
        slots_parts = []
        for idx, slot in enumerate(inspect_ship.weapon_slots):
            allowed = slot.get("allowed_types")
            if allowed:
                types_str = "/".join(allowed)
                slots_parts.append(f"H{idx+1}: [{types_str}]")
            else:
                slots_parts.append(f"H{idx+1}: [ALLE]")
        slots_str = f"WAFFENSLOTS ({inspect_ship.max_weapons}): " + " | ".join(slots_parts)
        slots_lbl = small_font.render(slots_str, True, (180, 215, 245))
        self.screen.blit(slots_lbl, (inspector_rect.x + 15, inspector_rect.y + 96))

        # Zeile 5: Waffentyp-Legende
        legend_str = "HINWEIS: LASER (Schildbrecher) | BEAM (Linienschaden) | MISSILE (Schildbypass) | ION (Systemlähmung)"
        self.screen.blit(small_font.render(legend_str, True, (130, 160, 195)), (inspector_rect.x + 15, inspector_rect.y + 118))

        # Action Buttons Leiste unten (Y = 532)
        self.btn_start = pygame.Rect(40, 532, 195, 42)
        self.btn_continue_game = pygame.Rect(250, 532, 195, 42)
        self.btn_options = pygame.Rect(460, 532, 195, 42)
        self.btn_quit = pygame.Rect(670, 532, 195, 42)

        has_save = SaveManager.has_savegame()

        self.draw_scifi_button(
            self.btn_start,
            "REISE STARTEN",
            is_hovered=self.btn_start.collidepoint(mx, my),
            primary_color=(0, 220, 130),
        )
        self.draw_scifi_button(
            self.btn_continue_game,
            "SPIELSTAND LADEN",
            is_hovered=self.btn_continue_game.collidepoint(mx, my),
            primary_color=(0, 180, 255),
            enabled=has_save,
        )
        self.draw_scifi_button(
            self.btn_options,
            "OPTIONEN & TON",
            is_hovered=self.btn_options.collidepoint(mx, my),
            primary_color=(180, 120, 255),
        )
        self.draw_scifi_button(
            self.btn_quit,
            "SPIEL BEENDEN",
            is_hovered=self.btn_quit.collidepoint(mx, my),
            primary_color=(255, 70, 70),
        )

        if self.data.current_state == STATE_OPTIONS:
            self.draw_options_menu()

    def draw_options_menu(self):
        pygame.draw.rect(self.screen, (20, 28, 42), (180, 50, 540, 480))
        pygame.draw.rect(self.screen, (100, 200, 255), (180, 50, 540, 480), 3)

        self.screen.blit(
            self.font.render("--- OPTIONEN & EINSTELLUNGEN ---", True, (100, 220, 255)),
            (290, 68),
        )

        game_ref = getattr(self, "game", None)
        mode_str = getattr(game_ref, "display_mode", "FULLSCREEN_WINDOWED") if game_ref else "FULLSCREEN_WINDOWED"
        res_idx = getattr(game_ref, "resolution_idx", 0) if game_ref else 0
        res_list = getattr(game_ref, "resolutions", RESOLUTIONS) if game_ref else RESOLUTIONS
        cur_res = res_list[res_idx] if res_idx < len(res_list) else (1920, 1080)
        sound_ref = getattr(game_ref, "sound", None) if game_ref else (getattr(self, "sound", None))
        audio_on = sound_ref.enabled if sound_ref else True

        master_v = sound_ref.master_volume if sound_ref else 1.0
        music_v = sound_ref.music_volume if sound_ref else 0.8
        sfx_v = sound_ref.sfx_volume if sound_ref else 0.7

        mode_labels = {
            "FULLSCREEN_WINDOWED": "Fullscreen Fenstermodus [STANDARD]",
            "WINDOWED": "Fenstermodus (Normales Fenster)",
            "FULLSCREEN": "Exklusives Vollbild (Hardware-Fullscreen)",
        }
        disp_mode_label = mode_labels.get(mode_str, mode_str)

        # 1. Anzeigemodus Button
        self.btn_toggle_fullscreen = pygame.Rect(210, 105, 480, 36)
        m_col = (30, 80, 100) if mode_str == "FULLSCREEN_WINDOWED" else ((40, 60, 90) if mode_str == "WINDOWED" else (70, 50, 90))
        pygame.draw.rect(self.screen, m_col, self.btn_toggle_fullscreen)
        pygame.draw.rect(self.screen, (0, 200, 255), self.btn_toggle_fullscreen, 2)
        fs_txt = pygame.font.SysFont(None, 17, bold=True).render(f"Anzeigemodus: {disp_mode_label}", True, (100, 255, 220))
        self.screen.blit(fs_txt, (self.btn_toggle_fullscreen.x + 18, self.btn_toggle_fullscreen.y + 10))

        # 2. Fensterauflösung
        self.btn_res_toggle = pygame.Rect(210, 148, 480, 36)
        pygame.draw.rect(self.screen, (40, 60, 90), self.btn_res_toggle)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_res_toggle, 2)
        res_txt = self.font.render(f"Auflösung: {cur_res[0]} x {cur_res[1]} (Klick = Wechseln)", True, (220, 240, 255))
        self.screen.blit(res_txt, (self.btn_res_toggle.x + 55, self.btn_res_toggle.y + 8))

        # 3. Audio Stummschalten Toggle
        self.btn_audio_toggle = pygame.Rect(210, 191, 480, 36)
        aud_col = (40, 80, 40) if audio_on else (80, 40, 40)
        pygame.draw.rect(self.screen, aud_col, self.btn_audio_toggle)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_audio_toggle, 2)
        aud_label = "Audio Hauptschalter: AN" if audio_on else "Audio Hauptschalter: STUMM"
        aud_color = (150, 240, 150) if audio_on else (255, 120, 120)
        audio_txt = self.font.render(aud_label, True, aud_color)
        self.screen.blit(audio_txt, (self.btn_audio_toggle.x + 140, self.btn_audio_toggle.y + 8))

        # --- LAUTSTÄRKE EINSTELLUNGEN ---
        # Helper to draw a volume row with [-] [ Bar ] [+]
        def draw_vol_row(y: int, label: str, val: float, btn_down_attr: str, btn_up_attr: str):
            lbl_surf = self.font.render(f"{label}: {int(val * 100)}%", True, (200, 235, 255))
            self.screen.blit(lbl_surf, (215, y + 6))

            btn_down = pygame.Rect(452, y, 34, 30)
            btn_up = pygame.Rect(648, y, 34, 30)
            setattr(self, btn_down_attr, btn_down)
            setattr(self, btn_up_attr, btn_up)

            pygame.draw.rect(self.screen, (50, 70, 100), btn_down)
            pygame.draw.rect(self.screen, (0, 200, 255), btn_down, 1)
            self.screen.blit(self.font.render("-", True, (255, 255, 255)), (btn_down.x + 12, btn_down.y + 5))

            pygame.draw.rect(self.screen, (50, 70, 100), btn_up)
            pygame.draw.rect(self.screen, (0, 200, 255), btn_up, 1)
            self.screen.blit(self.font.render("+", True, (255, 255, 255)), (btn_up.x + 10, btn_up.y + 5))

            # Progress Bar Background & Fill (capped strictly inside container)
            bar_rect = pygame.Rect(492, y + 4, 150, 22)
            pygame.draw.rect(self.screen, (15, 25, 40), bar_rect)
            pygame.draw.rect(self.screen, (80, 120, 160), bar_rect, 1)

            # Map 0.0 - 2.0 to 0 - 146 px width
            fill_width = int(min(146, max(0, 146 * (val / 2.0))))
            if fill_width > 0:
                fill_rect = pygame.Rect(494, y + 6, fill_width, 18)
                pygame.draw.rect(self.screen, (0, 220, 180), fill_rect)

        draw_vol_row(235, "Master (Gesamt)", master_v, "btn_master_down", "btn_master_up")
        draw_vol_row(273, "Musik (BGM)", music_v, "btn_music_down", "btn_music_up")
        draw_vol_row(311, "Effekte (SFX)", sfx_v, "btn_sfx_down", "btn_sfx_up")

        # 4. Auto-Speichern Toggle
        auto_save_on = getattr(self.data, "auto_save_enabled", False)
        self.btn_autosave_toggle = pygame.Rect(210, 350, 480, 34)
        as_col = (40, 80, 40) if auto_save_on else (80, 40, 40)
        pygame.draw.rect(self.screen, as_col, self.btn_autosave_toggle)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_autosave_toggle, 2)
        as_label = "Auto-Speichern bei Sprung: AN" if auto_save_on else "Auto-Speichern bei Sprung: AUS [MANUELL]"
        as_color = (150, 240, 150) if auto_save_on else (255, 200, 150)
        as_txt = self.font.render(as_label, True, as_color)
        self.screen.blit(as_txt, (self.btn_autosave_toggle.x + 60, self.btn_autosave_toggle.y + 7))

        # 5. Errungenschaften Button
        self.btn_achievements_menu = pygame.Rect(210, 390, 480, 34)
        pygame.draw.rect(self.screen, (35, 65, 95), self.btn_achievements_menu)
        pygame.draw.rect(self.screen, (255, 215, 0), self.btn_achievements_menu, 2)
        ach_btn_txt = self.font.render("ERRUNGENSCHAFTEN ANSEHEN", True, (255, 230, 100))
        self.screen.blit(ach_btn_txt, (self.btn_achievements_menu.x + 110, self.btn_achievements_menu.y + 7))

        # Steuerungshinweis
        ctrl_font = pygame.font.SysFont(None, 17)
        self.screen.blit(ctrl_font.render("Steuerung: S = Speichern | L = Laden | Pausieren = Leertaste | +/- = Lautstärke", True, (160, 180, 210)), (210, 432))

        # 6. Zurück Button
        self.btn_close_options = pygame.Rect(350, 460, 200, 40)
        pygame.draw.rect(self.screen, (70, 40, 40), self.btn_close_options)
        pygame.draw.rect(self.screen, COLOR_ENEMY_BORDER, self.btn_close_options, 2)
        close_txt = "Zurück zur Pause" if self.data.paused else "Zurück zum Menü"
        self.screen.blit(self.font.render(close_txt, True, (255, 200, 200)), (self.btn_close_options.x + 25, self.btn_close_options.y + 9))

    def draw_achievements_screen(self):
        bg_surf = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        bg_surf.fill((10, 16, 28, 245))
        self.screen.blit(bg_surf, (0, 0))

        pygame.draw.rect(self.screen, (18, 26, 42), (40, 20, 820, 560))
        pygame.draw.rect(self.screen, (0, 200, 255), (40, 20, 820, 560), 2)

        title_font = pygame.font.SysFont(None, 24, bold=True)
        sub_font = pygame.font.SysFont(None, 16, bold=True)
        small_font = pygame.font.SysFont(None, 14)

        # 1. Titel
        t_lbl = title_font.render("--- GALAKTISCHE ERRUNGENSCHAFTEN ---", True, (100, 220, 255))
        self.screen.blit(t_lbl, (LOGICAL_WIDTH // 2 - t_lbl.get_width() // 2, 28))

        # 2. Gesamt-Fortschrittsbalken
        ach_mgr = getattr(self.data, "achievements", None)
        ach_dict = ach_mgr.achievements if ach_mgr else {}
        total_count = len(ach_dict)
        unlocked_count = sum(1 for a in ach_dict.values() if a.get("unlocked", False))
        pct = (unlocked_count / total_count) if total_count > 0 else 0.0

        bar_rect = pygame.Rect(180, 54, 540, 20)
        pygame.draw.rect(self.screen, (15, 25, 40), bar_rect)
        pygame.draw.rect(self.screen, (80, 120, 160), bar_rect, 1)

        fill_w = int(536 * pct)
        if fill_w > 0:
            pygame.draw.rect(self.screen, (0, 220, 180), (182, 56, fill_w, 16))

        prog_str = f"Freigeschaltet: {unlocked_count} / {total_count} ({int(pct * 100)}%)"
        prog_lbl = small_font.render(prog_str, True, (255, 255, 255))
        self.screen.blit(prog_lbl, (bar_rect.x + (bar_rect.width - prog_lbl.get_width()) // 2, bar_rect.y + 3))

        # 3. Kategorie-Filter Tabs
        categories = ["ALLE", "KAMPF", "CREW", "SCHIFF", "ERKUNDUNG"]
        cur_cat = getattr(self.data, "achievement_category_filter", "ALLE")
        mx, my = self._logical_mouse_pos()

        for idx, cat in enumerate(categories):
            btn_tab = pygame.Rect(55 + idx * 158, 82, 150, 28)
            setattr(self, f"btn_ach_tab_{idx}", btn_tab)
            is_sel = (cat == cur_cat)
            is_hov = btn_tab.collidepoint(mx, my)

            t_bg = (30, 80, 120) if is_sel else ((24, 40, 62) if is_hov else (18, 28, 44))
            t_border = (0, 230, 255) if is_sel else ((100, 180, 240) if is_hov else (60, 90, 120))
            pygame.draw.rect(self.screen, t_bg, btn_tab)
            pygame.draw.rect(self.screen, t_border, btn_tab, 2 if is_sel else 1)

            t_txt = sub_font.render(cat, True, (255, 255, 255) if is_sel else (180, 210, 240))
            self.screen.blit(t_txt, (btn_tab.x + (btn_tab.width - t_txt.get_width()) // 2, btn_tab.y + 6))

        # 4. Gefilterte Achievements Liste
        filtered = [
            a for a in ach_dict.values()
            if cur_cat == "ALLE" or a.get("category", "KAMPF") == cur_cat
        ]

        cards_per_page = 6
        total_pages = max(1, (len(filtered) + cards_per_page - 1) // cards_per_page)
        cur_page = min(getattr(self.data, "achievement_page", 0), total_pages - 1)
        self.data.achievement_page = cur_page

        start_idx = cur_page * cards_per_page
        page_items = filtered[start_idx : start_idx + cards_per_page]

        # 2 Spalten x 3 Zeilen Grid
        for idx, a_data in enumerate(page_items):
            r_idx = idx // 2
            c_idx = idx % 2
            card_x = 55 + c_idx * 396
            card_y = 118 + r_idx * 122
            card_rect = pygame.Rect(card_x, card_y, 386, 114)

            unlocked = a_data.get("unlocked", False)
            raw_time = a_data.get("unlock_time", "")
            from managers.achievement_manager import format_german_datetime
            u_time = format_german_datetime(raw_time)

            if unlocked:
                bg_col = (20, 45, 68)
                border_col = (0, 230, 180)
                badge_bg = (30, 85, 65)
                badge_txt_col = (255, 220, 100)
                status_str = f"FREIGESCHALTET AM {u_time}" if u_time else "FREIGESCHALTET"
                title_col = (255, 255, 255)
                desc_col = (190, 230, 255)
            else:
                bg_col = (14, 20, 32)
                border_col = (50, 70, 95)
                badge_bg = (24, 32, 46)
                badge_txt_col = (130, 150, 175)
                status_str = "GESPERRT"
                title_col = (150, 168, 190)
                desc_col = (110, 125, 145)

            pygame.draw.rect(self.screen, bg_col, card_rect)
            pygame.draw.rect(self.screen, border_col, card_rect, 2 if unlocked else 1)

            # Badge oben
            badge_rect = pygame.Rect(card_x + 8, card_y + 8, card_rect.width - 16, 20)
            pygame.draw.rect(self.screen, badge_bg, badge_rect)
            pygame.draw.rect(self.screen, border_col, badge_rect, 1)
            b_lbl = small_font.render(status_str, True, badge_txt_col)
            self.screen.blit(b_lbl, (badge_rect.x + (badge_rect.width - b_lbl.get_width()) // 2, badge_rect.y + 3))

            # Titel
            t_str = a_data["title"]
            title_surf = sub_font.render(t_str, True, title_col)
            self.screen.blit(title_surf, (card_x + 12, card_y + 34))

            # Beschreibung (mit Wort-Umbruch)
            d_str = a_data["desc"]
            words = d_str.split(" ")
            line1, line2 = "", ""
            for w in words:
                if small_font.render((line1 + " " + w).strip(), True, desc_col).get_width() < card_rect.width - 24:
                    line1 = (line1 + " " + w).strip()
                else:
                    line2 = (line2 + " " + w).strip()

            self.screen.blit(small_font.render(line1, True, desc_col), (card_x + 12, card_y + 58))
            if line2:
                self.screen.blit(small_font.render(line2, True, desc_col), (card_x + 12, card_y + 76))

            # Kategorie Tag unten rechts
            cat_tag = small_font.render(f"[{a_data.get('category', 'KAMPF')}]", True, (100, 180, 240) if unlocked else (90, 110, 135))
            self.screen.blit(cat_tag, (card_x + card_rect.width - cat_tag.get_width() - 10, card_y + 92))

        # 5. Paginierung Buttons unten
        self.btn_ach_prev = pygame.Rect(180, 492, 120, 36)
        self.btn_ach_next = pygame.Rect(600, 492, 120, 36)
        page_txt = sub_font.render(f"Seite {cur_page + 1} von {total_pages}", True, (200, 235, 255))
        self.screen.blit(page_txt, (LOGICAL_WIDTH // 2 - page_txt.get_width() // 2, 501))

        self.draw_scifi_button(self.btn_ach_prev, "< Vorherige", is_hovered=self.btn_ach_prev.collidepoint(mx, my), enabled=(cur_page > 0))
        self.draw_scifi_button(self.btn_ach_next, "Nächste >", is_hovered=self.btn_ach_next.collidepoint(mx, my), enabled=(cur_page < total_pages - 1))

        # 6. Hauptmenü / Zurück Button
        self.btn_close_achievements = pygame.Rect(340, 532, 220, 38)
        self.draw_scifi_button(self.btn_close_achievements, "ZURÜCK ZUM MENÜ", is_hovered=self.btn_close_achievements.collidepoint(mx, my), primary_color=(0, 200, 255))




    def draw_event(self):
        ev_text = self.data.world.event_manager.current_event_text
        res_text = getattr(self.data.world.event_manager, "result_text", "")
        choices = self.data.world.event_manager.choices

        layout = calculate_event_layout(ev_text, res_text, choices, self.font)
        box_rect = layout["box_rect"]

        pygame.draw.rect(self.screen, (30, 40, 55), box_rect)
        pygame.draw.rect(self.screen, COLOR_BORDER, box_rect, 3)

        # Event-Text zeilenweise rendern
        curr_y = box_rect.y + 25
        for line in layout["ev_lines"]:
            lbl = self.font.render(line, True, (240, 240, 240))
            self.screen.blit(lbl, (box_rect.x + 30, curr_y))
            curr_y += 24

        # Result-Text (falls vorhanden)
        if res_text:
            curr_y = layout["res_start_y"]
            for line in layout["res_lines"]:
                lbl = self.font.render(line, True, (100, 255, 180))
                self.screen.blit(lbl, (box_rect.x + 30, curr_y))
                curr_y += 24

            cont_btn = layout["cont_btn"]
            pygame.draw.rect(self.screen, (40, 70, 100), cont_btn)
            pygame.draw.rect(self.screen, (100, 200, 255), cont_btn, 2)
            lbl = self.font.render("Weiter (Fortfahren)", True, (255, 255, 255))
            self.screen.blit(lbl, (cont_btn.x + (cont_btn.width - lbl.get_width()) // 2, cont_btn.y + 11))
            return

        if not choices:
            cont_btn = layout["cont_btn"]
            pygame.draw.rect(self.screen, (40, 70, 100), cont_btn)
            pygame.draw.rect(self.screen, (100, 200, 255), cont_btn, 2)
            lbl = self.font.render("Weiter (Fortfahren)", True, (255, 255, 255))
            self.screen.blit(lbl, (cont_btn.x + (cont_btn.width - lbl.get_width()) // 2, cont_btn.y + 11))
        else:
            from utils import can_afford_choice
            for idx, choice in enumerate(choices):
                btn = layout["choice_rects"][idx]
                is_blue = choice.get("is_blue", False)
                affordable = can_afford_choice(choice, self.data.player)

                if not affordable:
                    bg_color = (35, 40, 50)
                    border_color = (65, 70, 80)
                    text_color = (110, 120, 130)
                elif is_blue:
                    bg_color = (30, 90, 190)
                    border_color = (100, 200, 255)
                    text_color = (180, 240, 255)
                else:
                    bg_color = (45, 60, 85)
                    border_color = COLOR_BORDER
                    text_color = (220, 240, 255)

                pygame.draw.rect(self.screen, bg_color, btn)
                pygame.draw.rect(self.screen, border_color, btn, 2)

                ch_text = choice["text"]
                if not affordable:
                    ch_text += " [UNZUREICHENDE RESSOURCEN]"

                lbl = self.font.render(ch_text, True, text_color)
                # Falls Choice-Text zu lang ist, mit small_font rendern
                if lbl.get_width() > 570:
                    lbl = self.small_font.render(ch_text, True, text_color)
                self.screen.blit(lbl, (btn.x + 15, btn.y + (btn.height - lbl.get_height()) // 2))



    def draw_game_over(self):
        self.screen.blit(
            self.font.render(
                "DEIN SCHIFF WURDE ZERSTÖRT! [Klick für Neustart]",
                True,
                (255, 80, 80),
            ),
            (250, 250),
        )

    def draw_victory(self):
        self.screen.blit(
            self.font.render(
                "SIEG! Das Flaggschiff wurde vernichtet!",
                True,
                (100, 255, 100),
            ),
            (260, 220),
        )

        newly_unlocked = getattr(self.data.player, "newly_unlocked_ship", None)
        if newly_unlocked:
            self.screen.blit(
                self.font.render(
                    f"NEUES SCHIFF FREIGESCHALTET: {newly_unlocked}!",
                    True,
                    (255, 220, 100),
                ),
                (230, 260),
            )

        self.screen.blit(
            self.font.render(
                "[ Klick zum Fortfahren / Neustarten ]",
                True,
                (200, 220, 255),
            ),
            (260, 310),
        )
