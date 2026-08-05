import copy
import math
import random
import sys
from typing import Literal
import pygame

from classes.GameData import GameData
from classes.Crew import Crew
import classes.EventManager
from classes.Projectile import Projectile
import classes.Reactor
from classes.Room import Room
from classes.ShieldSystem import ShieldSystem
import classes.StarMap
from classes.ShipModel import ENEMY_BOSS, ENEMY_SCOUT, PLAYER_SHIP
from classes.Weapon import Weapon
from managers.combat_manager import CombatManager
from managers.input_manager import InputManager
from managers.map_manager import MapManager
from managers.render_manager import RenderManager
from managers.shop_manager import ShopManager
from managers.state_manager import StateManager
from settings import *

pygame.init()
screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(
    "FTL Prototype - Erweiterte Schusslinien & Autofire"
)
clock: pygame.time.Clock = pygame.time.Clock()

data = GameData()

shop_manager = ShopManager(data)
map_manager = MapManager(data)
state_manager = StateManager(data)
input_manager = InputManager(data, shop_manager, map_manager)
combat_manager = CombatManager(data)
render_manager = RenderManager(screen, data)

# --- MAIN LOOP ---
while data.running:
  dt = clock.tick(60) / 1000.0

  input_manager.update()

  combat_manager.update(dt)
  
  render_manager.draw()
  
  pygame.display.flip()

  # --- RENDERING ---

  

#  if current_state == STATE_MAP:
#    data.event_manager.current_event_type = None
#    data.star_map.draw(screen)  #[cite: 12]
#
#  elif current_state == STATE_EVENT:
#    pygame.draw.rect(screen, (30, 40, 55), (150, 150, 600, 250))
#    pygame.draw.rect(screen, COLOR_BORDER, (150, 150, 600, 250), 3)  #[cite: 2]
#    screen.blit(
#        font.render(data.event_manager.current_event_text, True, (240, 240, 240)),  #[cite: 5]
#        (180, 200),
#    )
#    screen.blit(
#        font.render(
#            "[ Klick zum Fortfahren ]", True, COLOR_SELECTED
#        ),  #[cite: 2]
#        (340, 330),
#    )
#
#  
#
#  elif current_state == STATE_COMBAT:
#    data.player_reactor.draw(screen, 30, 45)  #[cite: 8]
#
#    for r in data.player_ship.rooms:
#      r.draw(screen)  #[cite: 9]
#    for r in data.current_enemy_ship.rooms:
#      r.draw(screen)  #[cite: 9]
#
#    for c in data.player_crew:
#      c.draw(screen)  #[cite: 4]
#    for p in data.player_projectiles:
#      p.draw(screen)  #[cite: 7]
#
#    data.player_shield.draw_bubble(screen, (220, 245), 170)  #[cite: 10]
#    data.enemy_shield.draw_bubble(screen, (710, 245), 150)  #[cite: 10]
#
#    # NEU: Dauerhafte, sichtbare Schusslinien für jede aktiv zugewiesene Waffe zeichnen
#    for idx, (target_room, start_p, end_p) in data.player_weapon_targets.items():
#      w_name = data.player_weapons[idx].name if idx < len(data.player_weapons) else "Waffe"
#      color_line = (255, 100, 100) if idx == 1 else (100, 200, 255)
#      pygame.draw.line(screen, color_line, start_p, end_p, 2)
#      pygame.draw.circle(screen, color_line, end_p, 6, 2)
#
#    screen.blit(
#        font.render(
#            f"Spieler Hülle: {data.player_ship.hp}/{data.player_ship.max_hp} HP",
#            True,
#            (100, 255, 100),
#        ),
#        (60, 155),
#    )
#    current_evade = int(data.player_ship.rooms[2].current_power * 0.20 * 100)
#    screen.blit(
#        font.render(
#            f"Ausweichchance: {current_evade}%", True, (150, 200, 255)
#        ),
#        (60, 175),
#    )
#
#    screen.blit(
#        font.render(
#            f"Gegner Hülle: {data.current_enemy_ship.hp}/{data.current_enemy_ship.max_hp} HP",
#            True,
#            (255, 100, 100),
#        ),
#        (550, 155),
#    )
#
#    # Waffen-Anzeige mit Typenbezeichnung
#    weapon_ui_y = 310
#    screen.blit(
#        font.render("Waffensysteme:", True, (200, 200, 200)), (30, weapon_ui_y)
#    )
#    for i, w in enumerate(data.player_weapons):
#      bar_x, bar_y = 30 + i * 115, weapon_ui_y + 25
#      charge_ratio = w.current_charge / w.charge_time  #[cite: 13]
#      pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, 105, 15))
#      bar_color = (
#          COLOR_POWER_ACTIVE if w.is_ready() else COLOR_WEAPON_CHARGE  #[cite: 2, 13]
#      )
#      pygame.draw.rect(
#          screen, bar_color, (bar_x, bar_y, int(105 * charge_ratio), 15)
#      )
#      pygame.draw.rect(screen, COLOR_BORDER, (bar_x, bar_y, 105, 15), 1)  #[cite: 2]
#
#      # Zeige an, ob die Waffe ein Ziel hat
#      target_indicator = " [Z]" if i in data.player_weapon_targets else ""
#      lbl = font.render(f"{w.name}{target_indicator}", True, (200, 220, 255))
#      screen.blit(lbl, (bar_x, bar_y - 18))
#
#    pygame.draw.rect(screen, (50, 60, 80), btn_autofire)
#    pygame.draw.rect(
#        screen, COLOR_SELECTED if data.player_autofire_enabled else COLOR_BORDER, btn_autofire, 2
#    )  #[cite: 2]
#    autofire_txt = font.render(
#        f"Autofire: {'AN' if data.player_autofire_enabled else 'AUS'}",
#        True,
#        (100, 255, 100) if data.player_autofire_enabled else (200, 200, 200),
#    )
#    screen.blit(autofire_txt, (btn_autofire.x + 15, btn_autofire.y + 5))
#
#    if data.combat_msg_timer > 0.0:
#      msg_txt = font.render(data.combat_msg, True, COLOR_SELECTED)  #[cite: 2]
#      screen.blit(msg_txt, (SCREEN_WIDTH // 2 - 80, 140))
#
#    if data.is_player_targeting:
#      mx, my = pygame.mouse.get_pos()
#      pygame.draw.line(
#          screen, COLOR_PROJECTILE, data.player_targeting_start_pos, (mx, my), 2
#      )  #[cite: 2]
#      pygame.draw.circle(screen, COLOR_PROJECTILE, (mx, my), 5, 1)
#
#    if data.paused:
#      p_font = pygame.font.SysFont(None, 48)
#      p_txt = p_font.render("PAUSE", True, (255, 255, 100))
#      screen.blit(p_txt, (SCREEN_WIDTH // 2 - p_txt.get_width() // 2, 40))
#
#  elif current_state == STATE_GAME_OVER:
#    screen.blit(
#        font.render(
#            "DEIN SCHIFF WURDE ZERSTÖRT! [Klick für Neustart]",
#            True,
#            (255, 80, 80),
#        ),
#        (250, 250),
#    )
#
#  elif current_state == STATE_VICTORY:
#    screen.blit(
#        font.render(
#            "SIEG! Das Flaggschiff wurde vernichtet! [Klick für Neustart]",
#            True,
#            (100, 255, 100),
#        ),
#        (200, 250),
#    )
#
#  pygame.display.flip()
#
#pygame.quit()
#sys.exit()