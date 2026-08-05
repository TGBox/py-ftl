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
        self.btn_crew_toggle = pygame.Rect(750, 10, 130, 30)
        # Shop UI Buttons
        self.btn_repair = pygame.Rect(200, 140, 500, 38)  #[cite: 1]
        self.btn_fuel = pygame.Rect(200, 185, 500, 38)  #[cite: 1]
        self.btn_missiles = pygame.Rect(200, 230, 500, 38)  #[cite: 1]
        self.btn_upgrade_reactor = pygame.Rect(200, 275, 500, 38)  #[cite: 1]
        self.btn_buy_crew = pygame.Rect(200, 320, 500, 38)  #[cite: 1]
        self.btn_buy_weapon = pygame.Rect(200, 365, 500, 38)  #[cite: 1]
        self.btn_leave_shop = pygame.Rect(200, 420, 500, 38)  #[cite: 1]

    def draw(self):
        self.screen.fill(COLOR_BG)

        self.screen.blit(
              self.font.render(
                  f"Treibstoff: {self.data.player.fuel}  |  Raketen: {self.data.player.missiles}  |  Scrap: {self.data.player.scrap}  |"
                  f"  Hülle: {self.data.player.ship.hp}/{self.data.player.ship.max_hp}  |  Sektor:"
                  f" {self.data.world.star_map.sector}",  #[cite: 12]
                  True,
                  (255, 255, 255),
              ),
              (20, 15),
          )

        # Crew-Menü Button oben rechts
        if self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY):
            pygame.draw.rect(self.screen, (50, 70, 95), self.btn_crew_toggle)
            pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_crew_toggle, 2)
            lbl = self.font.render("Crew-Menü", True, (220, 240, 255))
            self.screen.blit(lbl, (self.btn_crew_toggle.x + 18, self.btn_crew_toggle.y + 6))

        if self.data.current_state == STATE_MAIN_MENU:
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

            name_lbl = self.font.render(f"{crew.name} ({crew.species})", True, (255, 255, 255))
            hp_lbl = self.font.render(f"HP: {int(crew.hp)}/{int(crew.max_hp)}", True, (100, 255, 100))

            if crew.species == "Engi":
                perk_str = "Perk: +100% Reparieren, -50% Kampfschaden"
                badge_col = (255, 180, 50)
            elif crew.species == "Mantis":
                perk_str = "Perk: +50% Kampfschaden, -40% Reparieren"
                badge_col = (80, 240, 80)
            else:
                perk_str = "Perk: Ausgewogene Standardwerte (+0%)"
                badge_col = (100, 180, 255)

            perk_lbl = self.font.render(perk_str, True, badge_col)

            # Umbenennen Button
            rename_btn = pygame.Rect(580, card_y + 15, 130, 35)
            pygame.draw.rect(self.screen, (60, 80, 110), rename_btn)
            pygame.draw.rect(self.screen, COLOR_BORDER, rename_btn, 1)
            self.screen.blit(self.font.render("Umbenennen", True, (220, 240, 255)), (rename_btn.x + 12, rename_btn.y + 8))

            self.screen.blit(name_lbl, (190, card_y + 10))
            self.screen.blit(hp_lbl, (360, card_y + 10))
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
            (self.btn_buy_weapon, "Zufallswaffe kaufen & fusionieren - 40 Scrap"),
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
        # 1. Reaktor zeichnen
        self.data.player.reactor.draw(self.screen, 30, 45)

        # 2. Räume zeichnen
        for r in self.data.player.ship.rooms:
            r.draw(self.screen)
        for r in self.data.enemy.ship.rooms:
            r.draw(self.screen)
            
        # 3. Crew zeichnen
        for c in self.data.player.crew:
            c.draw(self.screen)
            
        # 4. Schiffs-Hülle & Ausweichchance (UI)
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

    def draw_weapons(self):
        # 1. Dauerhafte Schusslinien (Weapon Targets)
        for idx, (_, start_p, end_p) in self.data.combat.weapon_targets.items():
            color_line = (255, 100, 100) if idx == 1 else (100, 200, 255)
            pygame.draw.line(self.screen, color_line, start_p, end_p, 2)
            pygame.draw.circle(self.screen, color_line, end_p, 6, 2)

        # 2. Zielen-Linie (beim aktiven Zielen mit Maus)
        if self.data.combat.is_targeting:
            mx, my = pygame.mouse.get_pos()
            pygame.draw.line(
                self.screen, COLOR_PROJECTILE, self.data.combat.start_pos, (mx, my), 2
            )
            pygame.draw.circle(self.screen, COLOR_PROJECTILE, (mx, my), 5, 1)

        # 3. Waffen-UI-Bars
        weapon_ui_y = 310
        self.screen.blit(
            self.font.render("Waffensysteme:", True, (200, 200, 200)), (30, weapon_ui_y)
        )
        for i, w in enumerate(self.data.player.weapons):
            bar_x, bar_y = 30 + i * 115, weapon_ui_y + 25
            charge_ratio = w.current_charge / w.charge_time
            pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, 105, 15))
            bar_color = (
                COLOR_POWER_ACTIVE if w.is_ready() else COLOR_WEAPON_CHARGE
            )
            pygame.draw.rect(
                self.screen, bar_color, (bar_x, bar_y, int(105 * charge_ratio), 15)
            )
            pygame.draw.rect(self.screen, COLOR_BORDER, (bar_x, bar_y, 105, 15), 1)

            # Zeige an, ob die Waffe ein Ziel hat
            target_indicator = " [Z]" if i in self.data.combat.weapon_targets else ""
            lbl = self.font.render(f"{w.name}{target_indicator}", True, (200, 220, 255))
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

    def draw_messages(self):
        # Temporäre Kampfnachrichten
        if self.data.combat.msg_timer > 0.0:
            msg_txt = self.font.render(self.data.combat.msg, True, COLOR_SELECTED)
            self.screen.blit(msg_txt, (SCREEN_WIDTH // 2 - 80, 140))
            
        # Pause Text (falls du pause in GameData gespeichert hast)
        if self.data.paused:
            p_font = pygame.font.SysFont(None, 48)
            p_txt = p_font.render("PAUSE", True, (255, 255, 100))
            self.screen.blit(p_txt, (SCREEN_WIDTH // 2 - p_txt.get_width() // 2, 40))
            
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

        if self.data.current_state == STATE_OPTIONS:
            self.draw_options_menu()

    def draw_options_menu(self):
        pygame.draw.rect(self.screen, (25, 35, 50), (200, 100, 500, 360))
        pygame.draw.rect(self.screen, (100, 200, 255), (200, 100, 500, 360), 3)

        self.screen.blit(
            self.font.render("--- EINSTELLUNGEN & GRAFIK ---", True, (100, 220, 255)),
            (320, 130),
        )

        self.btn_toggle_fullscreen = pygame.Rect(250, 190, 400, 45)
        pygame.draw.rect(self.screen, (50, 70, 100), self.btn_toggle_fullscreen)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_toggle_fullscreen, 2)
        fs_txt = self.font.render("Vollbildmodus Umschalten (Fullscreen)", True, (255, 255, 255))
        self.screen.blit(fs_txt, (self.btn_toggle_fullscreen.x + 35, self.btn_toggle_fullscreen.y + 12))

        self.btn_res_toggle = pygame.Rect(250, 255, 400, 45)
        pygame.draw.rect(self.screen, (50, 70, 100), self.btn_res_toggle)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_res_toggle, 2)
        res_txt = self.font.render("Fensterauflösung: 900 x 600", True, (220, 240, 255))
        self.screen.blit(res_txt, (self.btn_res_toggle.x + 75, self.btn_res_toggle.y + 12))

        self.btn_close_options = pygame.Rect(350, 380, 200, 42)
        pygame.draw.rect(self.screen, (70, 40, 40), self.btn_close_options)
        pygame.draw.rect(self.screen, COLOR_ENEMY_BORDER, self.btn_close_options, 2)
        self.screen.blit(self.font.render("Zurück zum Menü", True, (255, 200, 200)), (self.btn_close_options.x + 30, self.btn_close_options.y + 10))



    def draw_event(self):
        pygame.draw.rect(self.screen, (30, 40, 55), (150, 130, 600, 300))
        pygame.draw.rect(self.screen, COLOR_BORDER, (150, 130, 600, 300), 3)
        self.screen.blit(
            self.font.render(self.data.world.event_manager.current_event_text, True, (240, 240, 240)),
            (180, 170),
        )

        choices = self.data.world.event_manager.choices
        if not choices:
            self.screen.blit(
                self.font.render("[ Klick zum Fortfahren ]", True, COLOR_SELECTED),
                (340, 370),
            )
        else:
            for idx, choice in enumerate(choices):
                btn = pygame.Rect(180, 240 + idx * 48, 540, 38)
                is_blue = choice.get("is_blue", False)
                bg_color = (30, 90, 190) if is_blue else (50, 65, 90)
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
                "SIEG! Das Flaggschiff wurde vernichtet! [Klick für Neustart]",
                True,
                (100, 255, 100),
            ),
            (200, 250),
        )