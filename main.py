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
from classes.Room import Room
from classes.ShipModel import ENEMY_BOSS, ENEMY_SCOUT, PLAYER_SHIP
from classes.Weapon import Weapon
from settings import *

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 550
screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FTL Prototype - Erweiterter Kampf")
clock: pygame.time.Clock = pygame.time.Clock()


#class Weapon:
#
#  def __init__(self, name: str = "Laser", charge_time: float = 3.0) -> None:
#    self.name: str = name
#    self.charge_time: float = charge_time
#    self.current_charge: float = 0.0
#    self.auto_fire: bool = False
#
#  def update(self, dt: float, powered: bool) -> None:
#    if powered:
#      self.current_charge = min(self.charge_time, self.current_charge + dt)
#
#  def is_ready(self) -> bool:
#    return self.current_charge >= self.charge_time
#
#  def reset(self) -> None:
#    self.current_charge = 0.0


#class ShieldSystem:
#
#  def __init__(self, recharge_time: float = 4.0) -> None:
#    self.max_layers: int = 0
#    self.current_layers: int = 0
#    self.recharge_timer: float = 0.0
#    self.recharge_time: float = recharge_time
#
#  def update(self, dt: float, powered_layers: int) -> None:
#    self.max_layers = powered_layers
#    if self.current_layers > self.max_layers:
#      self.current_layers = self.max_layers
#
#    if self.current_layers < self.max_layers:
#      self.recharge_timer += dt
#      if self.recharge_timer >= self.recharge_time:
#        self.current_layers += 1
#        self.recharge_timer = 0.0
#    else:
#      self.recharge_timer = 0.0
#
#  def attempt_block(self) -> bool:
#    if self.current_layers > 0:
#      self.current_layers -= 1
#      self.recharge_timer = 0.0
#      return True
#    return False


#class Projectile:
#
#  def __init__(
#      self,
#      start_pos: tuple[int, int],
#      target_pos: tuple[int, int],
#      target_room: Room,
#      is_player_shot: bool,
#  ) -> None:
#    self.x: float = float(start_pos[0])
#    self.y: float = float(start_pos[1])
#    self.target_x: float = float(target_pos[0])
#    self.target_y: float = float(target_pos[1])
#    self.target_room: Room = target_room
#    self.is_player_shot: bool = is_player_shot
#    self.alive: bool = True
#
#    dx = self.target_x - self.x
#    dy = self.target_y - self.y
#    dist = math.hypot(dx, dy)
#    self.vx: float = (dx / dist) * 400.0 if dist != 0 else 0.0
#    self.vy: float = (dy / dist) * 400.0 if dist != 0 else 0.0
#
#  def update(self, dt: float) -> None:
#    self.x += self.vx * dt
#    self.y += self.vy * dt
#    if math.hypot(self.target_x - self.x, self.target_y - self.y) < 10:
#      self.alive = False
#
#  def draw(self, surface: pygame.Surface) -> None:
#    pygame.draw.circle(
#        surface, COLOR_PROJECTILE, (int(self.x), int(self.y)), 5
#    )


#class Crew:
#
#  def __init__(self, x: float, y: float) -> None:
#    self.x: float = x
#    self.y: float = y
#    self.radius: int = 12
#    self.selected: bool = False
#    self.target_pos: tuple[int, int] | None = None
#
#  def update(self, dt: float, rooms: list[Room]) -> None:
#    if self.target_pos:
#      tx, ty = self.target_pos
#      dx, dy = tx - self.x, ty - self.y
#      dist = math.hypot(dx, dy)
#      if dist < 120.0 * dt:
#        self.x, self.y = float(tx), float(ty)
#        self.target_pos = None
#      else:
#        self.x += (dx / dist) * 120.0 * dt
#        self.y += (dy / dist) * 120.0 * dt
#    else:
#      for room in rooms:
#        if room.rect.collidepoint(int(self.x), int(self.y)):
#          if room.health < room.max_health:
#            room.repair(25.0 * dt)
#          break
#
#  def draw(self, surface: pygame.Surface) -> None:
#    color = COLOR_SELECTED if self.selected else COLOR_CREW
#    pygame.draw.circle(
#        surface, color, (int(self.x), int(self.y)), self.radius
#    )


# --- GAME STATES ERWEITERUNG ---
STATE_GAME_OVER = "GAME_OVER"
STATE_VICTORY = "VICTORY"

# --- SETUP ---
star_map = classes.StarMap.StarMap()
event_mgr = classes.EventManager.EventManager()

fuel = 5
scrap = 20

reactor = classes.Reactor.Reactor(total_power=6)
enemy_reactor = classes.Reactor.Reactor(total_power=6) # <-- NEU hinzugefügt
player_ship = copy.deepcopy(PLAYER_SHIP)
current_enemy = copy.deepcopy(ENEMY_SCOUT)

player_shield = ShieldSystem()
enemy_shield = ShieldSystem()
crew_members = [Crew(340, 245), Crew(115, 245)]
player_weapons: list[Weapon] = [Weapon("Standard Laser", charge_time=3.0)]
enemy_weapon = Weapon("Enemy Laser", charge_time=4.5)

projectiles: list[Projectile] = []
combat_msg = ""
combat_msg_timer = 0.0
paused = False
running = True
is_targeting = False
targeting_weapon_idx = None
targeting_start_pos = (0, 0)

# Shop UI Buttons
btn_repair = pygame.Rect(200, 150, 500, 40)
btn_fuel = pygame.Rect(200, 205, 500, 40)
btn_upgrade_reactor = pygame.Rect(200, 260, 500, 40)
btn_buy_crew = pygame.Rect(200, 315, 500, 40)
btn_buy_weapon = pygame.Rect(200, 370, 500, 40)
btn_leave_shop = pygame.Rect(200, 435, 500, 40)

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
                # FIX: Dem Boss Energie geben
                for room in current_enemy.rooms:
                  room.current_power = 1
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
            player_weapons.append(Weapon("Schnellfeuer", charge_time=2.0))
        elif btn_leave_shop.collidepoint(mx, my):
          current_state = STATE_MAP

      elif current_state == STATE_EVENT:
        if event_mgr.current_event_type == "COMBAT":
          current_enemy = copy.deepcopy(ENEMY_SCOUT)
          # FIX: Dem Standardgegner Energie geben
          for room in current_enemy.rooms:
            room.current_power = 1
          current_state = STATE_COMBAT
        else:
          current_state = STATE_MAP

      elif current_state == STATE_COMBAT:
        if is_targeting:
          for e_room in current_enemy.rooms:
            if e_room.rect.collidepoint(mx, my):
              projectiles.append(
                  Projectile(targeting_start_pos, (mx, my), e_room, True)
              )
              if (
                  targeting_weapon_idx is not None
                  and targeting_weapon_idx < len(player_weapons)
              ):
                player_weapons[targeting_weapon_idx].reset()
              is_targeting = False
              break
          is_targeting = False
        else:
          # Waffen UI Anklicken zum Zielen
          weapon_room = player_ship.rooms[1]
          if weapon_room.rect.collidepoint(mx, my):
            for idx, w in enumerate(player_weapons):
              if w.is_ready():
                is_targeting = True
                targeting_weapon_idx = idx
                targeting_start_pos = weapon_room.rect.center
                break

        # Crew Auswahl & Steuerung
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
        # Neustart
        player_ship = copy.deepcopy(PLAYER_SHIP)
        star_map.sector = 1
        star_map.generate_map()
        fuel, scrap = 5, 20
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

    # Waffenaufladung basierend auf Strom im Waffenraum
    weapon_powered = player_ship.rooms[1].current_power > 0
    for w in player_weapons:
      w.update(dt, weapon_powered)

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
          )
      )
      enemy_weapon.reset()

    for p in projectiles[:]:
      p.update(dt)
      if not p.alive:
        if p.is_player_shot:
          # Ausweichberechnung Gegner (abhängig von Brücken-Energie)
          enemy_evade = current_enemy.rooms[2].current_power * 0.15
          if random.random() < enemy_evade:
            combat_msg = "FEIND IST AUSGEWICHEN!"
            combat_msg_timer = 1.5
          elif not enemy_shield.attempt_block():
            current_enemy.hp = max(0, current_enemy.hp - 1)
            # FIX: Gegnerischer Schaden zieht Energie aus dem Feind-Reaktor ab!
            p.target_room.apply_damage(35.0, enemy_reactor) 
        else:
          # Ausweichberechnung Spieler (abhängig von Brücken-Energie)
          player_evade = player_ship.rooms[2].current_power * 0.20
          if random.random() < player_evade:
            combat_msg = "AUSGEWICHEN!"
            combat_msg_timer = 1.5
          elif not player_shield.attempt_block():
            player_ship.hp = max(0, player_ship.hp - 1)
            p.target_room.apply_damage(35.0, reactor)

        projectiles.remove(p)

    # Sieges- und Niederlagebedingungen
    if current_enemy.hp <= 0:
      scrap += 20
      projectiles.clear()
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

  # Top Bar Info
  screen.blit(
      font.render(
          f"Treibstoff: {fuel}  |  Scrap: {scrap}  |  Hülle:"
          f" {player_ship.hp}/{player_ship.max_hp}  |  Sektor:"
          f" {star_map.sector}",
          True,
          (255, 255, 255),
      ),
      (30, 15),
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
    pygame.draw.rect(screen, (25, 30, 40), (150, 80, 600, 410))
    pygame.draw.rect(screen, COLOR_SHOP_NODE, (150, 80, 600, 410), 3)
    screen.blit(
        font.render("--- HÄNDLER-STATION ---", True, COLOR_SHOP_NODE), (340, 105)
    )

    for btn, text in [
        (btn_repair, "Hülle reparieren (+1 HP) - 2 Scrap"),
        (btn_fuel, "Treibstoff kaufen (+1 Fuel) - 3 Scrap"),
        (btn_upgrade_reactor, "Reaktor aufrüsten (+1 Power) - 15 Scrap"),
        (btn_buy_crew, "Crew-Mitglied anheuern - 25 Scrap"),
        (btn_buy_weapon, "Neue Waffe kaufen - 45 Scrap"),
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
    
    # --- FIX: Gesundheitsanzeigen wieder einfügen ---
    screen.blit(
        font.render(
            f"Spieler Hülle: {player_ship.hp}/{player_ship.max_hp} HP",
            True,
            (100, 255, 100),
        ),
        (60, 170),
    )
    # NEU: Dynamische Ausweichrate anzeigen
    current_evade = int(player_ship.rooms[2].current_power * 0.20 * 100)
    screen.blit(
        font.render(
            f"Ausweichchance: {current_evade}%",
            True,
            (150, 200, 255),
        ),
        (60, 185),
    )

    screen.blit(
        font.render(
            f"Gegner Hülle: {current_enemy.hp}/{current_enemy.max_hp} HP",
            True,
            (255, 100, 100),
        ),
        (550, 160),
    )

    # UI Waffenauflade-Status
    weapon_ui_y = 310
    screen.blit(
        font.render("Waffensysteme:", True, (200, 200, 200)), (30, weapon_ui_y)
    )
    for i, w in enumerate(player_weapons):
      bar_x, bar_y = 30 + i * 110, weapon_ui_y + 25
      charge_ratio = w.current_charge / w.charge_time
      pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, 100, 15))
      bar_color = (
          COLOR_POWER_ACTIVE if w.is_ready() else COLOR_WEAPON_CHARGE
      )
      pygame.draw.rect(
          screen, bar_color, (bar_x, bar_y, int(100 * charge_ratio), 15)
      )
      pygame.draw.rect(screen, COLOR_BORDER, (bar_x, bar_y, 100, 15), 1)

    if combat_msg_timer > 0.0:
      msg_txt = font.render(combat_msg, True, COLOR_SELECTED)
      screen.blit(msg_txt, (SCREEN_WIDTH // 2 - 80, 150))

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