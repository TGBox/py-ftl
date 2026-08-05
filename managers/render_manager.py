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
        title_font = pygame.font.SysFont(None, 72)
        title_txt = title_font.render("FTL KLON", True, (255, 255, 255))
        self.screen.blit(title_txt, (SCREEN_WIDTH // 2 - title_txt.get_width() // 2, 200))

        # Start-Button (als Instanzvariable speichern, damit der Input-Manager ihn nutzen kann)
        self.btn_start = pygame.Rect(SCREEN_WIDTH // 2 - 100, 350, 200, 50)
        pygame.draw.rect(self.screen, (50, 60, 80), self.btn_start)
        pygame.draw.rect(self.screen, COLOR_BORDER, self.btn_start, 2)
        
        btn_txt = self.font.render("Neues Spiel starten", True, (200, 255, 200))
        self.screen.blit(btn_txt, (self.btn_start.x + 25, self.btn_start.y + 15))

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
                btn = pygame.Rect(180, 260 + idx * 50, 540, 36)
                pygame.draw.rect(self.screen, (50, 65, 90), btn)
                pygame.draw.rect(self.screen, COLOR_BORDER, btn, 2)
                lbl = self.font.render(choice["text"], True, (220, 240, 255))
                self.screen.blit(lbl, (btn.x + 15, btn.y + 8))


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