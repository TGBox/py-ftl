import pygame

from classes.GameData import GameData
from settings import *

class RenderManager:

    def __init__(self, screen: pygame.Surface, data: GameData):
        self.screen = screen
        self.data = data
        self.load_assets()
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36, bold=True)
        # Top-Right Buttons
        self.btn_crew_toggle = pygame.Rect(750, 8, 130, 26)
        self.btn_doors_open_all = pygame.Rect(750, 38, 130, 26)
        self.btn_doors_close_all = pygame.Rect(750, 68, 130, 26)
        self.btn_airlocks_vent = pygame.Rect(750, 98, 130, 26)
        self.btn_help_toggle = pygame.Rect(750, 128, 130, 26)

        # Bottom Action Buttons
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

        self.assets = {}
        asset_defs = {
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
                                r, g, b, a = img.get_at((x, y))
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
                f"Sektor: {self.data.world.star_map.sector}"
            )
            lbl = pygame.font.SysFont(None, 20).render(status_str, True, (240, 245, 255))
            self.screen.blit(lbl, (b_rect.x + 10, b_rect.y + 4))

            # Buttons oben rechts (Sci-Fi Glassmorphism Style)
            raw_mx, raw_my = pygame.mouse.get_pos()
            mx, my = raw_mx, raw_my

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

        if getattr(self.data.player, "show_crew_menu", False):
            self.draw_crew_menu()

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

            self.screen.blit(perk_lbl, (190, card_y + 35))

        close_btn = pygame.Rect(370, 465, 160, 38)
        pygame.draw.rect(self.screen, (70, 40, 40), close_btn)
        pygame.draw.rect(self.screen, COLOR_ENEMY_BORDER, close_btn, 2)
        self.screen.blit(self.font.render("Schließen", True, (255, 200, 200)), (close_btn.x + 40, close_btn.y + 10))


            
    def draw_combat(self):

        self.draw_rooms()

        self.draw_projectiles()

        self.draw_shields()

        self.draw_weapons()

        self.draw_messages()
        
    def draw_map(self):
        self.data.world.star_map.draw(self.screen)       
    def draw_shop(self):
        shop_mgr = getattr(self.game, "shop_manager", None) or getattr(self.data, "shop_manager", None)
        pygame.draw.rect(self.screen, (20, 30, 45), (80, 60, 740, 480))
        pygame.draw.rect(self.screen, COLOR_SHOP_NODE, (80, 60, 740, 480), 3)

        self.screen.blit(
            self.font.render("--- HÄNDLER-STATION ---", True, COLOR_SHOP_NODE),
            (340, 75),
        )

        small_font = pygame.font.SysFont(None, 20)
        items_left = [
            (pygame.Rect(100, 120, 340, 32), "Hülle reparieren (+1 HP) - 2 Scrap"),
            (pygame.Rect(100, 154, 340, 32), "Treibstoff kaufen (+1 Fuel) - 3 Scrap"),
            (pygame.Rect(100, 188, 340, 32), "Raketen kaufen (+3 Raketen) - 6 Scrap"),
            (pygame.Rect(100, 222, 340, 32), "Reaktor aufrüsten (+1 Power) - 15 Scrap"),
            (pygame.Rect(100, 256, 340, 32), "Crew-Mitglied anheuern - 25 Scrap"),
            (pygame.Rect(100, 290, 340, 32), "Schiff-Layout umbauen - 15 Scrap"),
        ]
        for btn, text in items_left:
            pygame.draw.rect(self.screen, (40, 50, 70), btn)
            pygame.draw.rect(self.screen, COLOR_BORDER, btn, 2)
            self.screen.blit(self.font.render(text, True, (220, 220, 220)), (btn.x + 12, btn.y + 6))

        self.screen.blit(self.font.render("Waffen & Augmentationen:", True, (255, 220, 100)), (460, 95))
        catalog = getattr(shop_mgr, "catalog_stock", []) if shop_mgr else []
        for idx, item in enumerate(catalog):
            item_btn = pygame.Rect(460, 120 + idx * 58, 340, 52)
            pygame.draw.rect(self.screen, (35, 55, 80), item_btn)
            pygame.draw.rect(self.screen, (100, 200, 255), item_btn, 2)

            if item.get("type") == "AUGMENT":
                name_lbl = self.font.render(f"{item['name']} (AUGMENT)", True, (240, 240, 255))
                stats_lbl = small_font.render(item.get("desc", ""), True, (180, 220, 240))
            else:
                w_type = item.get("w_type", "WEAPON")
                sub = item.get("subtype", "STANDARD")
                sub_tag = f" [{sub}]" if sub != "STANDARD" else ""
                name_lbl = self.font.render(f"{item['name']} ({w_type}){sub_tag}", True, (240, 240, 255))

                if sub == "BIO":
                    eff_txt = f"Crew Dmg: {int(item.get('crew_damage', 60))} | Ladezeit: {item.get('charge_time', 0)}s"
                elif sub == "FIRE":
                    eff_txt = f"Dmg: {int(item.get('damage', 0))} | Brand: {int(item.get('fire_chance', 0)*100)}% | Ladezeit: {item.get('charge_time', 0)}s"
                elif sub == "BREACH":
                    eff_txt = f"Dmg: {int(item.get('damage', 0))} | Bruch: {int(item.get('breach_chance', 0)*100)}% | Ladezeit: {item.get('charge_time', 0)}s"
                elif sub == "STUN":
                    eff_txt = f"Dmg: {int(item.get('damage', 0))} | Stun: {int(item.get('stun_duration', 0))}s | Ladezeit: {item.get('charge_time', 0)}s"
                else:
                    eff_txt = f"Dmg: {int(item.get('damage', 0))} | Pierce: {item.get('shield_pierce', 0)} | Ladezeit: {item.get('charge_time', 0)}s"

                stats_lbl = small_font.render(eff_txt, True, (180, 220, 240))
            price_lbl = self.font.render(f"{item['price']} Scrap", True, (255, 220, 100))

            self.screen.blit(name_lbl, (item_btn.x + 10, item_btn.y + 4))
            self.screen.blit(stats_lbl, (item_btn.x + 10, item_btn.y + 28))
            self.screen.blit(price_lbl, (item_btn.x + item_btn.width - 95, item_btn.y + 14))

        self.screen.blit(self.font.render("Eingebaute Waffen (Klick zum Verkaufen für 50% Scrap):", True, (200, 220, 255)), (100, 335))
        max_slots = getattr(self.data.player.ship, "max_weapons", 3)
        slots = getattr(self.data.player.ship, "weapon_slots", [])

        for idx in range(max_slots):
            card_x = 100 + idx * 245
            card_rect = pygame.Rect(card_x, 365, 230, 68)
            pygame.draw.rect(self.screen, (30, 40, 55), card_rect)
            pygame.draw.rect(self.screen, COLOR_BORDER, card_rect, 1)

            slot_info = slots[idx] if idx < len(slots) else {}
            allowed = slot_info.get("allowed_types")
            allowed_txt = ", ".join(allowed) if allowed else "Alle"

            if idx < len(self.data.player.weapons):
                w = self.data.player.weapons[idx]
                w_sub = getattr(w, "subtype", "STANDARD")
                w_sub_tag = f" [{w_sub}]" if w_sub != "STANDARD" else ""
                refund = max(15, 15 * w.level)
                lbl_name = small_font.render(f"Slot {idx+1}: {w.name}{w_sub_tag}", True, (100, 255, 180))
                lbl_allow = small_font.render(f"Erlaubt: {allowed_txt}", True, (160, 180, 200))
                self.screen.blit(lbl_name, (card_rect.x + 8, card_rect.y + 6))
                self.screen.blit(lbl_allow, (card_rect.x + 8, card_rect.y + 24))

                sell_btn = pygame.Rect(card_rect.x + 10, card_rect.y + 42, 210, 22)
                pygame.draw.rect(self.screen, (80, 40, 40), sell_btn)
                pygame.draw.rect(self.screen, (255, 100, 100), sell_btn, 1)
                lbl_sell = small_font.render(f"Verkaufen (+{refund} Scrap)", True, (255, 200, 200))
                self.screen.blit(lbl_sell, (sell_btn.x + 30, sell_btn.y + 3))
            else:
                lbl_empty = small_font.render(f"Slot {idx+1}: [ LEER ]", True, (150, 150, 150))
                lbl_allow = small_font.render(f"Erlaubt: {allowed_txt}", True, (160, 180, 200))
                self.screen.blit(lbl_empty, (card_rect.x + 8, card_rect.y + 12))
                self.screen.blit(lbl_allow, (card_rect.x + 8, card_rect.y + 35))

        btn_leave = pygame.Rect(320, 490, 260, 40)
        pygame.draw.rect(self.screen, (60, 40, 40), btn_leave)
        pygame.draw.rect(self.screen, COLOR_ENEMY_BORDER, btn_leave, 2)
        self.screen.blit(self.font.render("Shop verlassen", True, (255, 200, 200)), (btn_leave.x + 60, btn_leave.y + 10))

        # Modal 1: Layout-Umbau Modal Overlay
        is_swap_mode = getattr(shop_mgr, "layout_swap_mode", False) if shop_mgr else False
        first_r = getattr(shop_mgr, "layout_swap_first_room", None) if shop_mgr else None

        if is_swap_mode:
            overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 15, 25, 210))
            self.screen.blit(overlay, (0, 0))

            title_txt = "SCHIFF-LAYOUT UMBAUEN (15 SCRAP)"
            subtitle_txt = f"1. Raum: {first_r.name.upper()} | Klicke auf den 2. Raum zum Tauschen!" if first_r else "KLICKE AUF ZWEI RÄUME, UM DEREN SYSTEME ZU TAUSCHEN:"

            t_lbl = self.font.render(title_txt, True, (255, 220, 100))
            st_lbl = small_font.render(subtitle_txt, True, (100, 220, 255))
            self.screen.blit(t_lbl, (240, 30))
            self.screen.blit(st_lbl, (220, 58))

            # Spielerschiff Räume zeichnen
            for r in self.data.player.ship.rooms:
                is_first = (r == first_r)
                border_color = (255, 220, 0) if is_first else (100, 200, 255)
                fill_color = (70, 70, 20) if is_first else (30, 45, 65)

                pygame.draw.rect(self.screen, fill_color, r.rect)
                pygame.draw.rect(self.screen, border_color, r.rect, 3 if is_first else 2)

                lbl_r = small_font.render(r.name, True, (255, 255, 255))
                self.screen.blit(lbl_r, (r.rect.x + 6, r.rect.y + 6))

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

                if not has_w:
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
        # 0. Schiffshüllen (Player & Enemy Hull Sprites)
        if "kestrel_hull" in self.assets and self.data.player.ship.rooms:
            p_rooms = self.data.player.ship.rooms
            min_x = min(r.rect.left for r in p_rooms) - 25
            min_y = min(r.rect.top for r in p_rooms) - 25
            self.screen.blit(self.assets["kestrel_hull"], (min_x, min_y))

        if "enemy_scout" in self.assets and self.data.enemy.ship.rooms:
            e_rooms = self.data.enemy.ship.rooms
            min_x = min(r.rect.left for r in e_rooms) - 25
            min_y = min(r.rect.top for r in e_rooms) - 25
            self.screen.blit(self.assets["enemy_scout"], (min_x, min_y))

        # 1. Reaktor zeichnen (links am Rand)
        self.data.player.reactor.draw(self.screen, 15, 45)

        # Kompakte Infoboxen OBERHALB der Schiffe (Absolut KEINE Überlappungen!)
        small_font = pygame.font.SysFont(None, 17, bold=True)

        p_box = pygame.Rect(10, 34, 225, 22)
        p_surf = pygame.Surface((p_box.width, p_box.height), pygame.SRCALPHA)
        p_surf.fill((14, 25, 42, 210))
        self.screen.blit(p_surf, (p_box.x, p_box.y))
        pygame.draw.rect(self.screen, (0, 200, 255), p_box, 1)

        evade_val = int(self.data.player.ship.rooms[2].current_power * 0.20 * 100) if len(self.data.player.ship.rooms) > 2 else 10
        p_lbl = small_font.render(f"Spieler Hülle: {self.data.player.ship.hp}/{self.data.player.ship.max_hp} HP  |  Ausw: {evade_val}%", True, (130, 240, 170))
        self.screen.blit(p_lbl, (p_box.x + 8, p_box.y + 4))

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
        for r in self.data.player.ship.rooms:
            r.draw(self.screen)

        # Sensor-Stufen Prüfung
        sens_room = next((r for r in self.data.player.ship.rooms if r.name == "Sensoren"), None)
        sensor_power = sens_room.current_power if sens_room else 1

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
            for c in getattr(self.data.combat_manager, "enemy_crew", []):
                c.draw(self.screen)

        # 4. Drohnen im Raum & Orbit zeichnen
        import math

        if getattr(self.data.combat, "combat_drone_active", False):
            ang = getattr(self.data.combat, "drone_orbit_angle", 0.0)
            d_x = int(670 + math.cos(ang) * 160)
            d_y = int(240 + math.sin(ang) * 110)
            pygame.draw.circle(self.screen, (255, 100, 50), (d_x, d_y), 9)
            pygame.draw.circle(self.screen, (255, 255, 255), (d_x, d_y), 9, 2)
            d_lbl = small_font.render("KAMPFDROHNE", True, (255, 160, 100))
            self.screen.blit(d_lbl, (d_x - d_lbl.get_width() // 2, d_y - 18))

        if getattr(self.data.combat, "repair_drone_active", False):
            rx, ry = getattr(self.data.combat, "repair_drone_pos", (160.0, 245.0))
            pygame.draw.rect(self.screen, (160, 190, 220), (int(rx) - 10, int(ry) - 10, 20, 20))
            pygame.draw.rect(self.screen, (50, 220, 100), (int(rx) - 10, int(ry) - 10, 20, 20), 2)
            r_lbl = small_font.render("REP-DROHNE", True, (100, 255, 100))
            self.screen.blit(r_lbl, (int(rx) - r_lbl.get_width() // 2, int(ry) + 12))

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

        if sensor_power >= 3:
            s3_font = pygame.font.SysFont(None, 12, bold=True)
            for e_r in self.data.enemy.ship.rooms:
                p_str = f"PWR: {e_r.current_power}/{e_r.max_power}"
                p_lbl = s3_font.render(p_str, True, (100, 220, 255))
                self.screen.blit(p_lbl, (e_r.rect.x + 4, e_r.rect.bottom - 14))

    def draw_shields(self):
        # Schilde zeichnen (mit den festen Koordinaten aus deinem alten Code)
        self.data.player.shield.draw_bubble(self.screen, (220, 245), 170)
        self.data.enemy.shield.draw_bubble(self.screen, (710, 245), 150)

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
            pygame.draw.line(self.screen, color_line, self.data.combat.start_pos, (mx, my), 2)
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

        # 4. Untere Aktions-Buttons (Sci-Fi Glassmorphism Style)
        raw_mx, raw_my = pygame.mouse.get_pos()
        mx, my = raw_mx, raw_my

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

        self.draw_scifi_button(
            self.btn_recall,
            "ZURÜCKBEAMEN",
            is_hovered=self.btn_recall.collidepoint(mx, my),
            primary_color=(240, 120, 50),
            enabled=(has_boarders and tp_cd <= 0),
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
            self.screen.blit(b_lbl, (SCREEN_WIDTH // 2 - b_lbl.get_width() // 2, 45))

        # Solar Flare Flash
        sf_flash = getattr(self.data.combat, "solar_flare_flash", 0.0)
        if sf_flash > 0.0:
            flash_surf = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
            alpha = int(min(200, sf_flash * 350))
            flash_surf.fill((255, 140, 0, alpha))
            self.screen.blit(flash_surf, (0, 0))

        # Umweltgefahr Banner
        current_node = self.data.world.star_map.current_node
        hazard = getattr(current_node, "hazard_type", "NONE") if current_node else "NONE"
        if hazard == "SOLAR_FLARE":
            sf_timer = getattr(self.data.combat, "solar_flare_timer", 20.0)
            h_lbl = self.font.render(f"SONNEN-ERUPTION IN: {int(sf_timer)}s", True, (255, 160, 50))
            self.screen.blit(h_lbl, (SCREEN_WIDTH // 2 - h_lbl.get_width() // 2, 75))
        elif hazard == "ASTEROID_FIELD":
            h_lbl = self.font.render("UMWELTGEFAHR: ASTEROIDENFELD", True, (180, 200, 240))
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
            
    def draw_scifi_button(
        self,
        rect: pygame.Rect,
        text: str,
        is_active: bool = False,
        is_hovered: bool = False,
        primary_color: tuple[int, int, int] = (0, 200, 255),
        enabled: bool = True,
    ):
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

        raw_mx, raw_my = pygame.mouse.get_pos()
        mx, my = raw_mx, raw_my

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

        # 5 Schiffskarten
        self.btn_ship_kestrel = pygame.Rect(45, 95, 155, 275)
        self.btn_ship_kreuzer = pygame.Rect(210, 95, 155, 275)
        self.btn_ship_tarnschiff = pygame.Rect(375, 95, 155, 275)
        self.btn_ship_zoltan = pygame.Rect(540, 95, 155, 275)
        self.btn_ship_fed = pygame.Rect(705, 95, 155, 275)

        selected_name = getattr(self.data.player.ship, "name", "Kestrel")

        ships_info = [
            (self.btn_ship_kestrel, "Kestrel", 15, 3, 4, 3),
            (self.btn_ship_kreuzer, "Kreuzer", 18, 4, 6, 4),
            (self.btn_ship_tarnschiff, "Tarnschiff", 12, 3, 3, 3),
            (self.btn_ship_zoltan, "Zoltan-Fregatte", 14, 4, 4, 4),
            (self.btn_ship_fed, "Federations-Kreuzer", 20, 4, 5, 4),
        ]

        unlocked = getattr(self.data.player, "unlocked_ships", ["Kestrel"])

        for btn, name, hp, weapons, crew, rooms_count in ships_info:
            is_sel = name == selected_name
            is_unlocked = name in unlocked
            is_hov = btn.collidepoint(mx, my)

            c_surf = pygame.Surface((btn.width, btn.height), pygame.SRCALPHA)
            if is_sel:
                c_surf.fill((25, 45, 70, 220))
                border_col = (0, 220, 255)
            elif is_hov:
                c_surf.fill((20, 35, 55, 200))
                border_col = (100, 200, 255)
            else:
                c_surf.fill((14, 22, 38, 190))
                border_col = (60, 80, 110)

            self.screen.blit(c_surf, (btn.x, btn.y))
            pygame.draw.rect(self.screen, border_col, btn, 3 if is_sel else (2 if is_hov else 1))

            name_disp = name if len(name) <= 12 else name[:11] + "."
            name_txt = self.font.render(name_disp, True, (255, 255, 255) if is_sel else (210, 220, 240))
            self.screen.blit(name_txt, (btn.x + 12, btn.y + 12))

            pygame.draw.line(
                self.screen, border_col, (btn.x + 10, btn.y + 38), (btn.x + btn.width - 10, btn.y + 38), 1
            )

            hp_txt = self.font.render(f"Hülle: {hp} HP", True, (140, 230, 160))
            w_txt = self.font.render(f"Waffen: {weapons}", True, (240, 220, 130))
            c_txt = self.font.render(f"Crew: {crew}", True, (130, 210, 255))

            self.screen.blit(hp_txt, (btn.x + 12, btn.y + 48))
            self.screen.blit(w_txt, (btn.x + 12, btn.y + 72))
            self.screen.blit(c_txt, (btn.x + 12, btn.y + 96))

            lbl_rooms = pygame.font.SysFont(None, 14).render("RAUM-LAYOUT:", True, (160, 180, 210))
            self.screen.blit(lbl_rooms, (btn.x + 12, btn.y + 124))
            for r in range(rooms_count):
                rx = btn.x + 12 + r * 32
                ry = btn.y + 142
                pygame.draw.rect(self.screen, (35, 60, 90), (rx, ry, 26, 26))
                pygame.draw.rect(self.screen, (0, 200, 255) if is_sel else (100, 130, 160), (rx, ry, 26, 26), 1)

            for c in range(min(crew, 4)):
                cx = btn.x + 20 + c * 30
                cy = btn.y + 185
                c_color = (0, 230, 140) if is_sel else (80, 160, 120)
                pygame.draw.circle(self.screen, c_color, (cx, cy), 8)

            sel_btn_rect = pygame.Rect(btn.x + 10, btn.y + 225, btn.width - 20, 36)
            if is_sel:
                self.draw_scifi_button(sel_btn_rect, "GEWÄHLT", is_active=True, primary_color=(0, 230, 140))
            elif is_unlocked:
                self.draw_scifi_button(sel_btn_rect, "WÄHLEN", is_hovered=is_hov, primary_color=(0, 180, 255))
            else:
                self.draw_scifi_button(sel_btn_rect, "GESPERRT", enabled=False)

        # Action Buttons Leiste unten
        self.btn_start = pygame.Rect(60, 395, 240, 44)
        self.btn_continue_game = pygame.Rect(330, 395, 240, 44)
        self.btn_options = pygame.Rect(600, 395, 240, 44)

        from managers.save_manager import SaveManager

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

        if self.data.current_state == STATE_OPTIONS:
            self.draw_options_menu()

    def draw_options_menu(self):
        pygame.draw.rect(self.screen, (20, 28, 42), (180, 70, 540, 440))
        pygame.draw.rect(self.screen, (100, 200, 255), (180, 70, 540, 440), 3)

        self.screen.blit(
            self.font.render("--- OPTIONEN & EINSTELLUNGEN ---", True, (100, 220, 255)),
            (290, 95),
        )

        # Read dynamic state from game reference
        game_ref = getattr(self, "game", None)
        is_fs = getattr(game_ref, "is_fullscreen", False) if game_ref else False
        res_idx = getattr(game_ref, "resolution_idx", 0) if game_ref else 0
        from settings import RESOLUTIONS
        cur_res = RESOLUTIONS[res_idx] if res_idx < len(RESOLUTIONS) else (900, 600)
        sound_ref = getattr(game_ref, "sound", None) if game_ref else None
        audio_on = sound_ref.enabled if sound_ref else True

        # 1. Vollbild
        self.btn_toggle_fullscreen = pygame.Rect(220, 140, 460, 44)
        fs_col = (60, 100, 60) if is_fs else (40, 60, 90)
        pygame.draw.rect(self.screen, fs_col, self.btn_toggle_fullscreen)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_toggle_fullscreen, 2)
        fs_label = "Vollbild: AN" if is_fs else "Vollbild: AUS (Fenster)"
        fs_txt = self.font.render(fs_label, True, (100, 255, 100) if is_fs else (255, 255, 255))
        self.screen.blit(fs_txt, (self.btn_toggle_fullscreen.x + 130, self.btn_toggle_fullscreen.y + 12))

        # 2. Fensterauflösung
        self.btn_res_toggle = pygame.Rect(220, 195, 460, 44)
        pygame.draw.rect(self.screen, (40, 60, 90), self.btn_res_toggle)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_res_toggle, 2)
        res_txt = self.font.render(f"Auflösung: {cur_res[0]} x {cur_res[1]} (Klick = Wechseln)", True, (220, 240, 255))
        self.screen.blit(res_txt, (self.btn_res_toggle.x + 55, self.btn_res_toggle.y + 12))

        # 3. Audio & Soundeffekte
        self.btn_audio_toggle = pygame.Rect(220, 250, 460, 44)
        aud_col = (40, 80, 40) if audio_on else (80, 40, 40)
        pygame.draw.rect(self.screen, aud_col, self.btn_audio_toggle)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_audio_toggle, 2)
        aud_label = "Audio & SFX: AN" if audio_on else "Audio & SFX: AUS (Stumm)"
        aud_color = (150, 240, 150) if audio_on else (255, 120, 120)
        audio_txt = self.font.render(aud_label, True, aud_color)
        self.screen.blit(audio_txt, (self.btn_audio_toggle.x + 130, self.btn_audio_toggle.y + 12))

        # 4. Verschlüsselter Spielstand
        self.btn_autosave_toggle = pygame.Rect(220, 305, 460, 44)
        pygame.draw.rect(self.screen, (40, 60, 90), self.btn_autosave_toggle)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_autosave_toggle, 2)
        save_txt = self.font.render("Verschlüsselter Spielstand: Aktiviert (AES-256)", True, (200, 220, 255))
        self.screen.blit(save_txt, (self.btn_autosave_toggle.x + 30, self.btn_autosave_toggle.y + 12))

        # Steuerungshinweis
        ctrl_font = pygame.font.SysFont(None, 18)
        self.screen.blit(ctrl_font.render("Steuerung: S = Speichern | L = Laden | Pausieren = Leertaste", True, (160, 180, 210)), (230, 365))

        # 5. Zurück Button
        self.btn_close_options = pygame.Rect(350, 440, 200, 45)
        pygame.draw.rect(self.screen, (70, 40, 40), self.btn_close_options)
        pygame.draw.rect(self.screen, COLOR_ENEMY_BORDER, self.btn_close_options, 2)
        close_txt = "Zurück zur Pause" if self.data.paused else "Zurück zum Menü"
        self.screen.blit(self.font.render(close_txt, True, (255, 200, 200)), (self.btn_close_options.x + 25, self.btn_close_options.y + 12))




    def draw_event(self):
        pygame.draw.rect(self.screen, (30, 40, 55), (120, 100, 660, 380))
        pygame.draw.rect(self.screen, COLOR_BORDER, (120, 100, 660, 380), 3)

        ev_text = self.data.world.event_manager.current_event_text
        self.screen.blit(
            self.font.render(ev_text, True, (240, 240, 240)),
            (150, 130),
        )

        res_text = getattr(self.data.world.event_manager, "result_text", "")
        if res_text:
            self.screen.blit(
                self.font.render(res_text, True, (100, 255, 180)),
                (150, 175),
            )
            cont_btn = pygame.Rect(280, 400, 340, 42)
            pygame.draw.rect(self.screen, (40, 70, 100), cont_btn)
            pygame.draw.rect(self.screen, (100, 200, 255), cont_btn, 2)
            lbl = self.font.render("Weiter (Fortfahren)", True, (255, 255, 255))
            self.screen.blit(lbl, (cont_btn.x + (cont_btn.width - lbl.get_width()) // 2, cont_btn.y + 11))
            return

        choices = self.data.world.event_manager.choices
        if not choices:
            cont_btn = pygame.Rect(280, 400, 340, 42)
            pygame.draw.rect(self.screen, (40, 70, 100), cont_btn)
            pygame.draw.rect(self.screen, (100, 200, 255), cont_btn, 2)
            lbl = self.font.render("Weiter (Fortfahren)", True, (255, 255, 255))
            self.screen.blit(lbl, (cont_btn.x + (cont_btn.width - lbl.get_width()) // 2, cont_btn.y + 11))
        else:
            for idx, choice in enumerate(choices):
                btn_y = 200 + idx * 44
                btn = pygame.Rect(150, btn_y, 600, 38)
                is_blue = choice.get("is_blue", False)
                bg_color = (30, 90, 190) if is_blue else (45, 60, 85)
                border_color = (100, 200, 255) if is_blue else COLOR_BORDER
                text_color = (180, 240, 255) if is_blue else (220, 240, 255)

                pygame.draw.rect(self.screen, bg_color, btn)
                pygame.draw.rect(self.screen, border_color, btn, 2)
                lbl = self.font.render(choice["text"], True, text_color)
                self.screen.blit(lbl, (btn.x + 15, btn.y + 10))



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