import pygame

from classes.GameData import GameData
from settings import *

class RenderManager:

    def __init__(self, screen: pygame.Surface, data: GameData):
        self.screen = screen
        self.data = data
        self.screen.fill(COLOR_BG)  #[cite: 2]
        self.font = pygame.font.SysFont(None, 24)
        self.btn_autofire = pygame.Rect(710, 520, 160, 30)
        self.btn_teleport = pygame.Rect(710, 480, 160, 30)
        self.btn_recall = pygame.Rect(540, 480, 160, 30)
        self.btn_cloak = pygame.Rect(370, 480, 160, 30)
        self.btn_crew_toggle = pygame.Rect(750, 10, 130, 30)
        # Shop UI Buttons
        self.btn_repair = pygame.Rect(200, 140, 500, 38)  #[cite: 1]
        self.btn_fuel = pygame.Rect(200, 185, 500, 38)  #[cite: 1]
        self.btn_missiles = pygame.Rect(200, 230, 500, 38)  #[cite: 1]
        self.btn_upgrade_reactor = pygame.Rect(200, 275, 500, 38)  #[cite: 1]
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
        # Door UI Buttons
        self.btn_doors_open_all = pygame.Rect(750, 45, 130, 26)
        self.btn_doors_close_all = pygame.Rect(750, 75, 130, 26)
        self.btn_airlocks_vent = pygame.Rect(750, 105, 130, 26)
        self.btn_cloak = pygame.Rect(370, 480, 160, 30)
        self.btn_combat_drone = pygame.Rect(200, 480, 160, 30)
        self.btn_repair_drone = pygame.Rect(30, 480, 160, 30)
        self.btn_crew_toggle = pygame.Rect(750, 10, 130, 30)
        self.btn_help_toggle = pygame.Rect(750, 135, 130, 26)

    def draw(self):
        self.screen.fill(COLOR_BG)

        self.screen.blit(
            self.font.render(
                f"Treibstoff: {self.data.player.fuel}  |  Raketen: {self.data.player.missiles}  |  Drohnen: {getattr(self.data.player, 'drone_parts', 5)}  |  Scrap: {self.data.player.scrap}  |"
                f"  Hülle: {self.data.player.ship.hp}/{self.data.player.ship.max_hp}  |  Sektor:"
                f" {self.data.world.star_map.sector}",
                True,
                (255, 255, 255),
            ),
            (20, 15),
        )

        # Crew-Menü & Tür-Steuerung Buttons oben rechts
        if self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY):
            pygame.draw.rect(self.screen, (50, 70, 95), self.btn_crew_toggle)
            pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_crew_toggle, 2)
            lbl = self.font.render("Crew-Menü", True, (220, 240, 255))
            self.screen.blit(lbl, (self.btn_crew_toggle.x + 18, self.btn_crew_toggle.y + 6))

            for btn, text, col in [
                (self.btn_doors_open_all, "Türen auf [O]", (40, 70, 95)),
                (self.btn_doors_close_all, "Türen zu [L]", (75, 40, 45)),
                (self.btn_airlocks_vent, "Vakuum [V]", (30, 80, 100)),
            ]:
                pygame.draw.rect(self.screen, col, btn)
                pygame.draw.rect(self.screen, COLOR_BORDER, btn, 1)
                d_lbl = self.font.render(text, True, (220, 240, 255))
                self.screen.blit(d_lbl, (btn.x + (btn.width - d_lbl.get_width()) // 2, btn.y + 4))

            # [?] HILFE Button
            pygame.draw.rect(self.screen, (80, 60, 120), self.btn_help_toggle)
            pygame.draw.rect(self.screen, (180, 140, 255), self.btn_help_toggle, 1)
            h_lbl = self.font.render("[?] HILFE [H]", True, (240, 220, 255))
            self.screen.blit(h_lbl, (self.btn_help_toggle.x + (self.btn_help_toggle.width - h_lbl.get_width()) // 2, self.btn_help_toggle.y + 4))

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

        elif self.data.current_state == STATE_GAME_OVER:
            self.draw_game_over()

        elif self.data.current_state == STATE_VICTORY:
            self.draw_victory()

        if getattr(self.data.player, "show_crew_menu", False):
            self.draw_crew_menu()

        # Taktische Pause Banner (SPACE)
        if self.data.paused and not getattr(self.data, "show_pause_menu", False):
            banner_rect = pygame.Rect(LOGICAL_WIDTH // 2 - 160, 42, 320, 26)
            pygame.draw.rect(self.screen, (30, 40, 60), banner_rect)
            pygame.draw.rect(self.screen, (255, 220, 100), banner_rect, 2)
            p_lbl = self.font.render("--- PAUSE (TAKTISCHER MODUS) ---", True, (255, 255, 100))
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
            (pygame.Rect(100, 120, 340, 36), "Hülle reparieren (+1 HP) - 2 Scrap"),
            (pygame.Rect(100, 162, 340, 36), "Treibstoff kaufen (+1 Fuel) - 3 Scrap"),
            (pygame.Rect(100, 204, 340, 36), "Raketen kaufen (+3 Raketen) - 6 Scrap"),
            (pygame.Rect(100, 246, 340, 36), "Reaktor aufrüsten (+1 Power) - 15 Scrap"),
            (pygame.Rect(100, 288, 340, 36), "Crew-Mitglied anheuern - 25 Scrap"),
        ]
        for btn, text in items_left:
            pygame.draw.rect(self.screen, (40, 50, 70), btn)
            pygame.draw.rect(self.screen, COLOR_BORDER, btn, 2)
            self.screen.blit(self.font.render(text, True, (220, 220, 220)), (btn.x + 12, btn.y + 8))

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

        btn_leave = pygame.Rect(320, 485, 260, 40)
        pygame.draw.rect(self.screen, (60, 40, 40), btn_leave)
        pygame.draw.rect(self.screen, COLOR_ENEMY_BORDER, btn_leave, 2)
        self.screen.blit(self.font.render("Shop verlassen", True, (255, 200, 200)), (btn_leave.x + 60, btn_leave.y + 10))

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
    def draw_rooms(self):
        # 1. Reaktor zeichnen
        self.data.player.reactor.draw(self.screen, 30, 45)

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

        # 5. Schiffs-Hülle & Ausweichchance (UI)
        self.screen.blit(
            self.font.render(
                f"Spieler Hülle: {self.data.player.ship.hp}/{self.data.player.ship.max_hp} HP",
                True,
                (100, 255, 100),
            ),
            (60, 155),
        )
        current_evade = int(self.data.player.ship.rooms[2].current_power * 0.20 * 100)
        self.screen.blit(
            self.font.render(
                f"Ausweichchance: {current_evade}%", True, (150, 200, 255)
            ),
            (60, 175),
        )
        self.screen.blit(
            self.font.render(
                f"Gegner Hülle: {self.data.enemy.ship.hp}/{self.data.enemy.ship.max_hp} HP",
                True,
                (255, 100, 100),
            ),
            (550, 155),
        )

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
            pygame.draw.line(
                self.screen, color_line, self.data.combat.start_pos, (mx, my), 2
            )
            pygame.draw.circle(self.screen, color_line, (mx, my), 7, 2)
            w_badge = self.font.render(f"W{t_idx+1}", True, color_line)
            self.screen.blit(w_badge, (mx + 10, my - 8))

        # 3. Waffen-UI-Bars
        weapon_ui_y = 485
        self.screen.blit(
            self.font.render("Waffensysteme:", True, (200, 200, 200)), (30, weapon_ui_y)
        )
        small_font = pygame.font.SysFont(None, 18)
        for i, w in enumerate(self.data.player.weapons):
            bar_x, bar_y = 30 + i * 135, weapon_ui_y + 35
            charge_ratio = w.current_charge / w.charge_time
            pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, 120, 16))
            bar_color = (
                COLOR_POWER_ACTIVE if w.is_ready() else COLOR_WEAPON_CHARGE
            )
            pygame.draw.rect(
                self.screen, bar_color, (bar_x, bar_y, int(120 * charge_ratio), 16)
            )
            pygame.draw.rect(self.screen, COLOR_BORDER, (bar_x, bar_y, 120, 16), 1)

            # Zeige an, ob die Waffe ein Ziel hat (mit individueller Waffenfarbe)
            w_color = WEAPON_LINE_COLORS[i % len(WEAPON_LINE_COLORS)]
            target_indicator = f" [W{i+1}]" if i in self.data.combat.weapon_targets else ""
            lbl_color = w_color if i in self.data.combat.weapon_targets else (200, 220, 255)
            disp_name = w.name if len(w.name) <= 15 else w.name[:14] + "."
            lbl = small_font.render(f"{disp_name}{target_indicator}", True, lbl_color)
            self.screen.blit(lbl, (bar_x, bar_y - 18))

        # 4. Autofire Button (wird vom Manager gezeichnet, Logik in InputManager)
        pygame.draw.rect(self.screen, (50, 60, 80), self.btn_autofire)
        pygame.draw.rect(
            self.screen, COLOR_SELECTED if self.data.combat.autofire_enabled else COLOR_BORDER, self.btn_autofire, 2
        )
        autofire_txt = self.font.render(
            f"Autofire: {'AN' if self.data.combat.autofire_enabled else 'AUS'}",
            True,
            (100, 255, 100) if self.data.combat.autofire_enabled else (200, 200, 200),
        )
        self.screen.blit(autofire_txt, (self.btn_autofire.x + 15, self.btn_autofire.y + 5))

        # 5. Teleporter Entern & Recall Buttons
        tp_cooldown = getattr(self.data.combat, "teleport_cooldown", 0.0)
        is_tp_target = getattr(self.data.combat, "is_teleport_targeting", False)

        tp_color = (40, 140, 180) if tp_cooldown <= 0 else (40, 40, 50)
        border_color = (100, 255, 255) if is_tp_target else (COLOR_BORDER if tp_cooldown <= 0 else (70, 70, 70))
        pygame.draw.rect(self.screen, tp_color, self.btn_teleport)
        pygame.draw.rect(self.screen, border_color, self.btn_teleport, 2)

        tp_label = "Ziel wählen..." if is_tp_target else ("Entern [BEAM]" if tp_cooldown <= 0 else f"Entern ({int(tp_cooldown)}s)")
        tp_txt = self.font.render(tp_label, True, (255, 255, 255) if tp_cooldown <= 0 else (140, 140, 140))
        self.screen.blit(tp_txt, (self.btn_teleport.centerx - tp_txt.get_width() // 2, self.btn_teleport.centery - tp_txt.get_height() // 2))

        has_boarders = any(getattr(c, "is_boarding", False) for c in self.data.player.crew)
        rec_color = (180, 80, 40) if (has_boarders and tp_cooldown <= 0) else (40, 40, 50)
        pygame.draw.rect(self.screen, rec_color, self.btn_recall)
        pygame.draw.rect(self.screen, COLOR_BORDER if (has_boarders and tp_cooldown <= 0) else (70, 70, 70), self.btn_recall, 2)
        rec_txt = self.font.render("Zurückbeamen", True, (255, 255, 255) if (has_boarders and tp_cooldown <= 0) else (140, 140, 140))
        self.screen.blit(rec_txt, (self.btn_recall.centerx - rec_txt.get_width() // 2, self.btn_recall.centery - rec_txt.get_height() // 2))

        # 6. Tarnung [CLOAK] Button
        cloak_room = next((r for r in self.data.player.ship.rooms if r.name == "Tarnung"), None)
        cloak_active = getattr(self.data.combat, "cloak_active_timer", 0.0)
        cloak_cd = getattr(self.data.combat, "cloak_cooldown", 0.0)

        is_ready = cloak_room and cloak_room.current_power > 0 and cloak_cd <= 0.0 and cloak_active <= 0.0
        c_bg = (60, 40, 100) if cloak_active > 0 else ((30, 80, 120) if is_ready else (40, 40, 50))
        c_border = (180, 100, 255) if cloak_active > 0 else ((100, 220, 255) if is_ready else (70, 70, 70))
        pygame.draw.rect(self.screen, c_bg, self.btn_cloak)
        pygame.draw.rect(self.screen, c_border, self.btn_cloak, 2)

        c_lbl = f"Tarnung ({int(cloak_active)}s)" if cloak_active > 0 else ("Tarnung [CLOAK]" if is_ready else f"Tarnung ({int(cloak_cd)}s)")
        c_txt = self.font.render(c_lbl, True, (255, 255, 255) if is_ready or cloak_active > 0 else (140, 140, 140))
        self.screen.blit(c_txt, (self.btn_cloak.centerx - c_txt.get_width() // 2, self.btn_cloak.centery - c_txt.get_height() // 2))

        # 7. Drohnen Steuerungs-Buttons
        drone_room = next((r for r in self.data.player.ship.rooms if r.name == "Drohnen-Kontrolle"), None)
        drone_power = drone_room.current_power if drone_room else 0

        # Kampfdrohne Button
        c_active = getattr(self.data.combat, "combat_drone_active", False)
        c_bg = (180, 80, 40) if c_active else ((30, 70, 100) if drone_power >= 1 else (40, 40, 50))
        c_border = (255, 160, 50) if c_active else ((100, 220, 255) if drone_power >= 1 else (70, 70, 70))
        pygame.draw.rect(self.screen, c_bg, self.btn_combat_drone)
        pygame.draw.rect(self.screen, c_border, self.btn_combat_drone, 2)
        c_txt = self.font.render("Kampfdrohne [1E]" if not c_active else "Kampfdrohne [AKTIV]", True, (255, 255, 255) if drone_power >= 1 or c_active else (140, 140, 140))
        self.screen.blit(c_txt, (self.btn_combat_drone.centerx - c_txt.get_width() // 2, self.btn_combat_drone.centery - c_txt.get_height() // 2))

        # Reparaturdrohne Button
        r_active = getattr(self.data.combat, "repair_drone_active", False)
        r_bg = (40, 140, 80) if r_active else ((30, 70, 100) if drone_power >= 2 else (40, 40, 50))
        r_border = (100, 255, 150) if r_active else ((100, 220, 255) if drone_power >= 2 else (70, 70, 70))
        pygame.draw.rect(self.screen, r_bg, self.btn_repair_drone)
        pygame.draw.rect(self.screen, r_border, self.btn_repair_drone, 2)
        r_txt = self.font.render("Rep-Drohne [2E]" if not r_active else "Rep-Drohne [AKTIV]", True, (255, 255, 255) if drone_power >= 2 or r_active else (140, 140, 140))
        self.screen.blit(r_txt, (self.btn_repair_drone.centerx - r_txt.get_width() // 2, self.btn_repair_drone.centery - r_txt.get_height() // 2))

        # 8. Augmentations Badges
        augments = getattr(self.data.player, "augments", [])
        if augments:
            small_font = pygame.font.SysFont(None, 14, bold=True)
            for a_idx, aug_name in enumerate(augments):
                a_rect = pygame.Rect(30 + a_idx * 165, 520, 155, 24)
                pygame.draw.rect(self.screen, (30, 45, 65), a_rect)
                pygame.draw.rect(self.screen, (100, 200, 255), a_rect, 1)
                a_lbl = small_font.render(f"AUG: {aug_name}", True, (160, 230, 255))
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

        # Temporäre Kampfnachrichten
        if self.data.combat.msg_timer > 0.0:
            msg_txt = self.font.render(self.data.combat.msg, True, COLOR_SELECTED)
            self.screen.blit(msg_txt, (SCREEN_WIDTH // 2 - msg_txt.get_width() // 2, 140))

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
            
    def draw_main_menu(self):
        # Titel
        title_font = pygame.font.SysFont(None, 64)
        title_txt = title_font.render("FTL KLON - RAUMSCHIFF WÄHLEN", True, (255, 255, 255))
        self.screen.blit(title_txt, (SCREEN_WIDTH // 2 - title_txt.get_width() // 2, 70))

        # Schiffswahl Karten
        self.btn_ship_kestrel = pygame.Rect(50, 150, 150, 200)
        self.btn_ship_kreuzer = pygame.Rect(215, 150, 150, 200)
        self.btn_ship_tarnschiff = pygame.Rect(380, 150, 150, 200)
        self.btn_ship_zoltan = pygame.Rect(545, 150, 150, 200)
        self.btn_ship_fed = pygame.Rect(710, 150, 150, 200)

        selected_name = getattr(self.data.player.ship, "name", "Kestrel")

        for btn, name, hp, weapons, crew, rooms_count in [
            (self.btn_ship_kestrel, "Kestrel", 15, 3, 4, 3),
            (self.btn_ship_kreuzer, "Kreuzer", 18, 4, 6, 4),
            (self.btn_ship_tarnschiff, "Tarnschiff", 12, 3, 3, 3),
            (self.btn_ship_zoltan, "Zoltan-Fregatte", 14, 4, 4, 4),
            (self.btn_ship_fed, "Federations-Kreuzer", 20, 4, 5, 4),
        ]:
            is_sel = (name == selected_name)
            bg_col = (40, 70, 100) if is_sel else (30, 40, 55)
            border_col = (100, 220, 255) if is_sel else (80, 90, 110)

            pygame.draw.rect(self.screen, bg_col, btn)
            pygame.draw.rect(self.screen, border_col, btn, 3 if is_sel else 2)

            name_txt = self.font.render(name[:11], True, (255, 255, 255) if is_sel else (200, 200, 200))
            hp_txt = self.font.render(f"Hülle: {hp} HP", True, (150, 220, 150))
            w_txt = self.font.render(f"Waffen: {weapons}", True, (220, 220, 150))
            c_txt = self.font.render(f"Crew: {crew}", True, (150, 200, 255))
            sel_txt = self.font.render("[ GEWÄHLT ]" if is_sel else "[ WÄHLEN ]", True, (100, 255, 100) if is_sel else (150, 150, 150))

            self.screen.blit(name_txt, (btn.x + 10, btn.y + 10))
            self.screen.blit(hp_txt, (btn.x + 10, btn.y + 35))
            self.screen.blit(w_txt, (btn.x + 10, btn.y + 55))
            self.screen.blit(c_txt, (btn.x + 10, btn.y + 75))

            # Mini Layout-Vorschau (Raster-Vorschau)
            for r in range(rooms_count):
                rx = btn.x + 10 + r * 32
                ry = btn.y + 105
                pygame.draw.rect(self.screen, (60, 90, 120), (rx, ry, 28, 28))
                pygame.draw.rect(self.screen, (200, 220, 255), (rx, ry, 28, 28), 1)

            # Crew Icons Vorschau
            for c in range(min(crew, 4)):
                cx = btn.x + 18 + c * 30
                cy = btn.y + 148
                pygame.draw.circle(self.screen, (50, 200, 100), (cx, cy), 8)

            self.screen.blit(sel_txt, (btn.x + 10, btn.y + 172))

        # Start-Button & Optionen-Button
        self.btn_start = pygame.Rect(SCREEN_WIDTH // 2 - 190, 380, 180, 48)
        pygame.draw.rect(self.screen, (50, 120, 70), self.btn_start)
        pygame.draw.rect(self.screen, (100, 255, 100), self.btn_start, 2)
        self.screen.blit(self.font.render("Reise Starten", True, (255, 255, 255)), (self.btn_start.x + 35, self.btn_start.y + 14))

        self.btn_options = pygame.Rect(SCREEN_WIDTH // 2 + 10, 380, 180, 48)
        pygame.draw.rect(self.screen, (60, 75, 100), self.btn_options)
        pygame.draw.rect(self.screen, (120, 160, 220), self.btn_options, 2)
        self.screen.blit(self.font.render("Optionen", True, (220, 240, 255)), (self.btn_options.x + 50, self.btn_options.y + 14))

        from managers.save_manager import SaveManager
        if SaveManager.has_savegame():
            pygame.draw.rect(self.screen, (40, 80, 120), self.btn_continue_game)
            pygame.draw.rect(self.screen, (100, 200, 255), self.btn_continue_game, 2)
            cont_txt = self.font.render("Spiel Fortsetzen (Letzter Speicherstand)", True, (220, 240, 255))
            self.screen.blit(cont_txt, (self.btn_continue_game.x + (self.btn_continue_game.width - cont_txt.get_width()) // 2, self.btn_continue_game.y + 11))

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