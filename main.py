import copy
import math
import random
import sys
import pygame

from classes.Crew import Crew
import classes.EventManager
from classes.Projectile import Projectile
import classes.Reactor
from classes.ShieldSystem import ShieldSystem
import classes.StarMap
from classes.ShipModel import ENEMY_BOSS, ENEMY_SCOUT, PLAYER_SHIP
from classes.Weapon import Weapon
from settings import *

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 550
screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FTL Prototype - Erweiterter Kampf & Waffentypen")
clock: pygame.time.Clock = pygame.time.Clock()

# --- SETUP ---
STATE_GAME_OVER = "GAME_OVER"
STATE_VICTORY = "VICTORY"

star_map = classes.StarMap.StarMap()
event_mgr = classes.EventManager.EventManager()

fuel = 5
scrap = 20
missiles = 6  # NEU: Raketen-Munition

reactor = classes.Reactor.Reactor(total_power=6)
enemy_reactor = classes.Reactor.Reactor(total_power=6)

player_ship = copy.deepcopy(PLAYER_SHIP)
current_enemy = copy.deepcopy(ENEMY_SCOUT)

player_shield = ShieldSystem()
enemy_shield = ShieldSystem()
crew_members = [Crew(340, 245), Crew(115, 245)]

# Waffen-Palette des Spielers
player_weapons: list[Weapon] = [
    Weapon("Standard Laser", charge_time=3.0, w_type="LASER"),
    Weapon("Artemis Rakete", charge_time=4.0, w_type="MISSILE", ammo_cost=1),
]

enemy_weapon = Weapon("Gegner Laser", charge_time=4.5, w_type="LASER")

projectiles: list[Projectile] = []
combat_msg = ""
combat_msg_timer = 0.0
paused = False
running = True
is_targeting = False
targeting_weapon_idx = None
targeting_start_pos = (0, 0)

# NEU: Autofire & Ziel-Zuweisung für automatisches Schießen
autofire_enabled = False
btn_autofire = pygame.Rect(730, 310, 140, 30)
locked_enemy_room = None  # Das aktuell anvisierte Ziel für den Autofire-Modus

# Shop UI Buttons
btn_repair = pygame.Rect(200, 140, 500, 38)
btn_fuel = pygame.Rect(200, 185, 500, 38)
btn_missiles = pygame.Rect(200, 230, 500, 38)
btn_upgrade_reactor = pygame.Rect(200, 275, 500, 38)
btn_buy_crew = pygame.Rect(200, 320, 500, 38)
btn_buy_weapon = pygame.Rect(200, 365, 500, 38)
btn_leave_shop = pygame.Rect(200, 420, 500, 38)

# --- MAIN LOOP ---
while running:
  dt = clock.tick(60) / 1000.0

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
      paused = not paused

    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
      mx, my = pygame.mouse.get_pos()

      if current_state == STATE_MAP and star_map.current_node is not None:
        for node in star_map.current_node.connections:
          if math.hypot(mx - node.x, my - node.y) <= 18 and fuel > 0:
            fuel -= 1
            star_map.current_node = node
            node.visited = True

            if node.event_type == "EXIT":
              if star_map.sector == 3:
                current_enemy = copy.deepcopy(ENEMY_BOSS)
                for r in current_enemy.rooms:
                  r.current_power = 1
                current_state = STATE_COMBAT
              else:
                star_map.sector += 1
                star_map.generate_map()
              scrap += 10
            elif node.event_type == "SHOP":
              current_state = STATE_SHOP
            else:
              add_scrap, add_fuel = event_mgr.trigger_event(node.event_type)
              scrap += add_scrap
              fuel += add_fuel
              current_state = STATE_EVENT
            break

      elif current_state == STATE_SHOP:
        if btn_repair.collidepoint(mx, my):
          if scrap >= 2 and player_ship.hp < player_ship.max_hp:
            scrap -= 2
            player_ship.hp += 1
        elif btn_fuel.collidepoint(mx, my):
          if scrap >= 3:
            scrap -= 3
            fuel += 1
        elif btn_missiles.collidepoint(mx, my):
          if scrap >= 6:
            scrap -= 6
            missiles += 3
        elif btn_upgrade_reactor.collidepoint(mx, my):
          if scrap >= 15:
            scrap -= 15
            reactor.total_power += 1
            reactor.available_power += 1
        elif btn_buy_crew.collidepoint(mx, my):
          if scrap >= 25:
            scrap -= 25
            crew_members.append(Crew(300, 245))
        elif btn_buy_weapon.collidepoint(mx, my):
          if scrap >= 45 and len(player_weapons) < 3:
            scrap -= 45
            # Fügt eine Pike-Strahlenwaffe hinzu
            player_weapons.append(
                Weapon(
                    "Pike Strahl",
                    charge_time=5.0,
                    w_type="BEAM",
                    shield_pierce=1,
                    damage=25.0,
                )
            )
        elif btn_leave_shop.collidepoint(mx, my):
          current_state = STATE_MAP

      elif current_state == STATE_EVENT:
        if event_mgr.current_event_type == "COMBAT":
          current_enemy = copy.deepcopy(ENEMY_SCOUT)
          for r in current_enemy.rooms:
            r.current_power = 1
          current_state = STATE_COMBAT
        else:
          current_state = STATE_MAP

      elif current_state == STATE_COMBAT:
        # Prüfen, ob die Autofire-Checkbox geklickt wurde
        if btn_autofire.collidepoint(mx, my):
          autofire_enabled = not autofire_enabled
        else:
          if is_targeting:
            for e_room in current_enemy.rooms:
              if e_room.rect.collidepoint(mx, my):
                locked_enemy_room = e_room  # Ziel für Autofire speichern
                if targeting_weapon_idx is not None:
                  w = player_weapons[targeting_weapon_idx]
                  if w.ammo_cost > 0 and missiles < w.ammo_cost:
                    combat_msg = "KEINE RAKETEN MEHR!"
                    combat_msg_timer = 1.5
                  else:
                    if w.ammo_cost > 0:
                      missiles -= w.ammo_cost
                    weapon_room = player_ship.rooms[1]
                    projectiles.append(
                        Projectile(
                            weapon_room.rect.center,
                            e_room.rect.center,
                            e_room,
                            is_player_shot=True,
                            w_type=w.w_type,
                            shield_pierce=w.shield_pierce,
                            damage=w.damage,
                        )
                  )
                  w.reset()
              is_targeting = False
              break
            is_targeting = False
          else:
          # Anklicken der geladenen Waffen im UI
            weapon_room = player_ship.rooms[1]
            if weapon_room.rect.collidepoint(mx, my):
              for idx, w in enumerate(player_weapons):
                if w.is_ready():
                  is_targeting = True
                  targeting_weapon_idx = idx
                  targeting_start_pos = weapon_room.rect.center
                  break

        # Crew-Steuerung
        clicked_crew = False
        for c in crew_members:
          if math.hypot(mx - c.x, my - c.y) <= c.radius:
            for other_c in crew_members:
              other_c.selected = False
            c.selected = True
            clicked_crew = True
            break

        if not clicked_crew:
          has_selected = any(c.selected for c in crew_members)
          for room in player_ship.rooms:
            if room.rect.collidepoint(mx, my):
              if has_selected:
                for c in crew_members:
                  if c.selected:
                    c.target_pos = (mx, my)
              else:
                room.add_power(reactor)

      elif current_state in (STATE_GAME_OVER, STATE_VICTORY):
        player_ship = copy.deepcopy(PLAYER_SHIP)
        star_map.sector = 1
        star_map.generate_map()
        fuel, scrap, missiles = 5, 20, 6
        current_state = STATE_MAP

    elif (
        event.type == pygame.MOUSEBUTTONDOWN
        and event.button == 3
        and current_state == STATE_COMBAT
    ):
      mx, my = pygame.mouse.get_pos()
      has_selected = False
      for c in crew_members:
        if c.selected:
          c.selected = False
          has_selected = True

      if not has_selected:
        for room in player_ship.rooms:
          if room.rect.collidepoint(mx, my):
            room.remove_power(reactor)

  # --- LOGIK UPDATES ---
  if not paused and current_state == STATE_COMBAT:
    combat_msg_timer = max(0.0, combat_msg_timer - dt)

    for c in crew_members:
      c.update(dt, player_ship.rooms)

    player_shield.update(dt, player_ship.rooms[0].current_power)
    enemy_shield.update(dt, current_enemy.rooms[0].current_power)

    weapon_powered = player_ship.rooms[1].current_power > 0
    for w in player_weapons:
      w.update(dt, weapon_powered)
      
    # NEU: Automatisches Schießen (Autofire), wenn aktiv und Ziel gewählt ist
    if autofire_enabled and locked_enemy_room is not None:
      weapon_room = player_ship.rooms[1]
      for w in player_weapons:
        if w.is_ready():  #[cite: 13]
          if w.ammo_cost > 0 and missiles < w.ammo_cost:
            combat_msg = "KEINE RAKETEN MEHR!"
            combat_msg_timer = 1.5
          else:
            if w.ammo_cost > 0:
              missiles -= w.ammo_cost
            projectiles.append(
                Projectile(
                    weapon_room.rect.center,
                    locked_enemy_room.rect.center,
                    locked_enemy_room,
                    is_player_shot=True,
                    w_type=w.w_type,
                    shield_pierce=w.shield_pierce,
                    damage=w.damage,
                )
            )  #[cite: 1, 7]
            w.reset()  #[cite: 13]

    enemy_weapon.update(
        dt,
        current_enemy.rooms[1].current_power > 0
        and current_enemy.rooms[1].health > 20.0,
    )

    if enemy_weapon.is_ready():
      target_room = random.choice(player_ship.rooms)
      projectiles.append(
          Projectile(
              current_enemy.rooms[1].rect.center,
              target_room.rect.center,
              target_room=target_room,
              is_player_shot=False,
              w_type=enemy_weapon.w_type,
              shield_pierce=enemy_weapon.shield_pierce,
              damage=enemy_weapon.damage,
          )
      )
      enemy_weapon.reset()

    # Treffer- und Schadenslogik
    for p in projectiles[:]:
      p.update(dt)
      if not p.alive:
        if p.is_player_shot:
          enemy_evade = current_enemy.rooms[2].current_power * 0.15
          if random.random() < enemy_evade:
            combat_msg = "FEIND IST AUSGEWICHEN!"
            combat_msg_timer = 1.5
          else:
            hit_successful = False
            if p.w_type == "MISSILE":
              # Raketen ignorieren Schilde komplett
              hit_successful = True
            elif p.w_type == "BEAM":
              # Strahlen durchdringen Schilde, wenn Schildschichten <= Durchdringungswert
              if enemy_shield.current_layers <= p.shield_pierce:
                hit_successful = True
              else:
                enemy_shield.attempt_block()
            else:  # LASER
              if not enemy_shield.attempt_block():
                hit_successful = True

            if hit_successful:
              current_enemy.hp = max(0, current_enemy.hp - 1)
              p.target_room.apply_damage(p.damage, enemy_reactor)
        else:
          player_evade = player_ship.rooms[2].current_power * 0.20
          if random.random() < player_evade:
            combat_msg = "AUSGEWICHEN!"
            combat_msg_timer = 1.5
          else:
            hit_successful = False
            if p.w_type == "MISSILE":
              hit_successful = True
            elif p.w_type == "BEAM":
              if player_shield.current_layers <= p.shield_pierce:
                hit_successful = True
              else:
                player_shield.attempt_block()
            else:
              if not player_shield.attempt_block():
                hit_successful = True

            if hit_successful:
              player_ship.hp = max(0, player_ship.hp - 1)
              p.target_room.apply_damage(p.damage, reactor)

        projectiles.remove(p)

    if current_enemy.hp <= 0:
      scrap += 20
      missiles += 2  # Belohnung: Munition droppt beim gegnerischen Schiff
      projectiles.clear()
      locked_enemy_room = None  # Ziel beim Sieg zurücksetzen
      if star_map.sector == 3 and current_enemy.name == "Flaggschiff":
        current_state = STATE_VICTORY
      else:
        current_state = STATE_MAP

    if player_ship.hp <= 0:
      projectiles.clear()
      current_state = STATE_GAME_OVER

  # --- RENDERING ---
  screen.fill(COLOR_BG)
  font = pygame.font.SysFont(None, 24)

  # Top-Bar Statusanzeige
  screen.blit(
      font.render(
          f"Treibstoff: {fuel}  |  Raketen: {missiles}  |  Scrap: {scrap}  |"
          f"  Hülle: {player_ship.hp}/{player_ship.max_hp}  |  Sektor:"
          f" {star_map.sector}",
          True,
          (255, 255, 255),
      ),
      (20, 15),
  )

  if current_state == STATE_MAP:
    star_map.draw(screen)

  elif current_state == STATE_EVENT:
    pygame.draw.rect(screen, (30, 40, 55), (150, 150, 600, 250))
    pygame.draw.rect(screen, COLOR_BORDER, (150, 150, 600, 250), 3)
    screen.blit(
        font.render(event_mgr.current_event_text, True, (240, 240, 240)),
        (180, 200),
    )
    screen.blit(
        font.render("[ Klick zum Fortfahren ]", True, COLOR_SELECTED), (340, 330)
    )

  elif current_state == STATE_SHOP:
    pygame.draw.rect(screen, (25, 30, 40), (150, 70, 600, 430))
    pygame.draw.rect(screen, COLOR_SHOP_NODE, (150, 70, 600, 430), 3)
    screen.blit(
        font.render("--- HÄNDLER-STATION ---", True, COLOR_SHOP_NODE), (340, 90)
    )

    for btn, text in [
        (btn_repair, "Hülle reparieren (+1 HP) - 2 Scrap"),
        (btn_fuel, "Treibstoff kaufen (+1 Fuel) - 3 Scrap"),
        (btn_missiles, "Raketen kaufen (+3 Raketen) - 6 Scrap"),
        (btn_upgrade_reactor, "Reaktor aufrüsten (+1 Power) - 15 Scrap"),
        (btn_buy_crew, "Crew-Mitglied anheuern - 25 Scrap"),
        (btn_buy_weapon, "Strahlenwaffe (Pike) kaufen - 45 Scrap"),
    ]:
      pygame.draw.rect(screen, (40, 50, 70), btn)
      pygame.draw.rect(screen, COLOR_BORDER, btn, 2)
      screen.blit(
          font.render(text, True, (220, 220, 220)), (btn.x + 20, btn.y + 10)
      )

    pygame.draw.rect(screen, (60, 40, 40), btn_leave_shop)
    pygame.draw.rect(screen, COLOR_ENEMY_BORDER, btn_leave_shop, 2)
    screen.blit(
        font.render("Shop verlassen", True, (255, 200, 200)),
        (btn_leave_shop.x + 180, btn_leave_shop.y + 10),
    )

  elif current_state == STATE_COMBAT:
    reactor.draw(screen, 30, 45)

    for r in player_ship.rooms:
      r.draw(screen)
    for r in current_enemy.rooms:
      r.draw(screen)

    for c in crew_members:
      c.draw(screen)
    for p in projectiles:
      p.draw(screen)

    player_shield.draw_bubble(screen, (220, 245), 170)
    enemy_shield.draw_bubble(screen, (710, 245), 150)

    screen.blit(
        font.render(
            f"Spieler Hülle: {player_ship.hp}/{player_ship.max_hp} HP",
            True,
            (100, 255, 100),
        ),
        (60, 155),
    )
    current_evade = int(player_ship.rooms[2].current_power * 0.20 * 100)
    screen.blit(
        font.render(
            f"Ausweichchance: {current_evade}%", True, (150, 200, 255)
        ),
        (60, 175),
    )

    screen.blit(
        font.render(
            f"Gegner Hülle: {current_enemy.hp}/{current_enemy.max_hp} HP",
            True,
            (255, 100, 100),
        ),
        (550, 155),
    )

    # Waffen-Anzeige mit Typenbezeichnung
    weapon_ui_y = 310
    screen.blit(
        font.render("Waffensysteme:", True, (200, 200, 200)), (30, weapon_ui_y)
    )
    for i, w in enumerate(player_weapons):
      bar_x, bar_y = 30 + i * 115, weapon_ui_y + 25
      charge_ratio = w.current_charge / w.charge_time
      pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, 105, 15))
      bar_color = (
          COLOR_POWER_ACTIVE if w.is_ready() else COLOR_WEAPON_CHARGE
      )
      pygame.draw.rect(
          screen, bar_color, (bar_x, bar_y, int(105 * charge_ratio), 15)
      )
      pygame.draw.rect(screen, COLOR_BORDER, (bar_x, bar_y, 105, 15), 1)

      lbl = font.render(f"{w.name} [{w.w_type}]", True, (200, 220, 255))
      screen.blit(lbl, (bar_x, bar_y - 18))

    # NEU: Zeichnen der Autofire-Checkbox in der GUI
    pygame.draw.rect(
        screen, (50, 60, 80), btn_autofire
    )
    pygame.draw.rect(
        screen, COLOR_SELECTED if autofire_enabled else COLOR_BORDER, btn_autofire, 2
    )  #[cite: 2]
    autofire_txt = font.render(
        f"Autofire: {'AN' if autofire_enabled else 'AUS'}",
        True,
        (100, 255, 100) if autofire_enabled else (200, 200, 200),
    )
    screen.blit(autofire_txt, (btn_autofire.x + 15, btn_autofire.y + 5))

    if combat_msg_timer > 0.0:
      msg_txt = font.render(combat_msg, True, COLOR_SELECTED)
      screen.blit(msg_txt, (SCREEN_WIDTH // 2 - 80, 140))

    if is_targeting:
      mx, my = pygame.mouse.get_pos()
      pygame.draw.line(
          screen, COLOR_PROJECTILE, targeting_start_pos, (mx, my), 2
      )
      pygame.draw.circle(screen, COLOR_PROJECTILE, (mx, my), 5, 1)

    if paused:
      p_font = pygame.font.SysFont(None, 48)
      p_txt = p_font.render("PAUSE", True, (255, 255, 100))
      screen.blit(
          p_txt, (SCREEN_WIDTH // 2 - p_txt.get_width() // 2, 40)
      )

  elif current_state == STATE_GAME_OVER:
    screen.blit(
        font.render(
            "DEIN SCHIFF WURDE ZERSTÖRT! [Klick für Neustart]",
            True,
            (255, 80, 80),
        ),
        (250, 250),
    )

  elif current_state == STATE_VICTORY:
    screen.blit(
        font.render(
            "SIEG! Das Flaggschiff wurde vernichtet! [Klick für Neustart]",
            True,
            (100, 255, 100),
        ),
        (200, 250),
    )

  pygame.display.flip()

pygame.quit()
sys.exit()