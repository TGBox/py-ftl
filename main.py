from __future__ import annotations
from classes.ShipModel import *
import copy
import math
import random
import sys
import pygame

import classes.Reactor
import classes.EventManager
import classes.StarMap
from settings import *
from classes.Room import Room

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 550
screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FTL Prototype - Erweiterter Kampf")
clock: pygame.time.Clock = pygame.time.Clock()

class Weapon:

  def __init__(self, charge_time: float = 3.0) -> None:
    self.charge_time: float = charge_time
    self.current_charge: float = 0.0

  def update(self, dt: float, powered: bool) -> None:
    if powered:
      self.current_charge = min(self.charge_time, self.current_charge + dt)

  def is_ready(self) -> bool:
    return self.current_charge >= self.charge_time

  def reset(self) -> None:
    self.current_charge = 0.0


class ShieldSystem:

  def __init__(self, recharge_time: float = 4.0) -> None:
    self.max_layers: int = 0
    self.current_layers: int = 0
    self.recharge_timer: float = 0.0
    self.recharge_time: float = recharge_time

  def update(self, dt: float, powered_layers: int) -> None:
    self.max_layers = powered_layers

    # Falls Energie abgezogen wurde, maximale Schilde anpassen
    if self.current_layers > self.max_layers:
      self.current_layers = self.max_layers

    # Schild lädt Schritt für Schritt nach Ablauf der Ladezeit auf
    if self.current_layers < self.max_layers:
      self.recharge_timer += dt
      if self.recharge_timer >= self.recharge_time:
        self.current_layers += 1
        self.recharge_timer = 0.0
    else:
      self.recharge_timer = 0.0

  def attempt_block(self) -> bool:
    if self.current_layers > 0:
      self.current_layers -= 1
      self.recharge_timer = 0.0  # Lade-Timer bei Schildtreffer zurücksetzen
      return True
    return False


class Projectile:

  def __init__(
      self,
      start_pos: tuple[int, int],
      target_pos: tuple[int, int],
      target_room: Room,
      is_player_shot: bool,
  ) -> None:
    self.x: float = float(start_pos[0])
    self.y: float = float(start_pos[1])
    self.target_x: float = float(target_pos[0])
    self.target_y: float = float(target_pos[1])
    self.target_room: Room = target_room
    self.is_player_shot: bool = is_player_shot
    self.alive: bool = True

    dx = self.target_x - self.x
    dy = self.target_y - self.y
    dist = math.hypot(dx, dy)
    self.vx: float = (dx / dist) * 400.0 if dist != 0 else 0.0
    self.vy: float = (dy / dist) * 400.0 if dist != 0 else 0.0

  def update(self, dt: float) -> None:
    self.x += self.vx * dt
    self.y += self.vy * dt
    if math.hypot(self.target_x - self.x, self.target_y - self.y) < 10:
      self.alive = False

  def draw(self, surface: pygame.Surface) -> None:
    pygame.draw.circle(
        surface, COLOR_PROJECTILE, (int(self.x), int(self.y)), 5
    )


class Crew:

  def __init__(self, x: float, y: float) -> None:
    self.x: float = x
    self.y: float = y
    self.radius: int = 12
    self.selected: bool = False
    self.target_pos: tuple[int, int] | None = None

  def update(self, dt: float, rooms: list[Room]) -> None:
    if self.target_pos:
      tx, ty = self.target_pos
      dx, dy = tx - self.x, ty - self.y
      dist = math.hypot(dx, dy)
      if dist < 120.0 * dt:
        self.x, self.y = float(tx), float(ty)
        self.target_pos = None
      else:
        self.x += (dx / dist) * 120.0 * dt
        self.y += (dy / dist) * 120.0 * dt
    else:
      # Automatische Reparatur im aktuellen Raum
      for room in rooms:
        if room.rect.collidepoint(int(self.x), int(self.y)):
          if room.health < room.max_health:
            room.repair(25.0 * dt)
          break

  def draw(self, surface: pygame.Surface) -> None:
    color = COLOR_SELECTED if self.selected else COLOR_CREW
    pygame.draw.circle(
        surface, color, (int(self.x), int(self.y)), self.radius
    )


# --- SETUP ---
star_map = classes.StarMap.StarMap()
event_mgr = classes.EventManager.EventManager()

fuel = 5
scrap = 20
player_max_hp = 10
player_hp = 10

reactor = classes.Reactor.Reactor(total_power=6)
player_rooms = [
    Room("Schild", (60, 200, 110, 90)),
    Room("Waffen", (180, 200, 110, 90)),
    Room("Brücke", (300, 200, 90, 90), max_power=2),
]
enemy_rooms = [
    Room("Schild", (550, 200, 110, 90), is_enemy=True),
    Room("Waffen", (670, 200, 110, 90), is_enemy=True),
    Room("Brücke", (790, 200, 80, 90), is_enemy=True),
]

player_shield = ShieldSystem()
enemy_shield = ShieldSystem()
crew_members = [Crew(340, 245), Crew(115, 245)]
player_weapons: list[Weapon] = [Weapon(charge_time=3.0)]
enemy_weapon = Weapon(charge_time=4.5)

projectiles: list[Projectile] = []
enemy_hp = 10
combat_msg = ""
combat_msg_timer = 0.0
paused = False
running = True
is_targeting = False
targeting_start_pos = (0, 0)

# Buttons im Shop
btn_repair = pygame.Rect(200, 180, 500, 40)
btn_fuel = pygame.Rect(200, 235, 500, 40)
btn_upgrade_reactor = pygame.Rect(200, 290, 500, 40)
btn_leave_shop = pygame.Rect(200, 360, 500, 40)
btn_buy_crew = pygame.Rect(200, 235, 500, 40)
btn_buy_weapon = pygame.Rect(200, 290, 500, 40)

# Initialisiere die Waffen als Liste
player_weapons = [Weapon(charge_time=3.0)] # Passe den Import-Pfad für Weapon an, falls nötig

# Lege den Startgegner fest
current_enemy = copy.deepcopy(ENEMY_SCOUT)

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
              if star_map.sector == 3: # Sektor 3 ist der Endboss
                  current_enemy = copy.deepcopy(ENEMY_BOSS)
                  current_state = STATE_COMBAT
              else:
                  star_map.sector += 1
                  star_map.generate_map()
              scrap += 10  # Sektor-Bonus
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
          if scrap >= 2 and player_hp < player_max_hp:
            scrap -= 2
            player_hp += 1
        elif btn_fuel.collidepoint(mx, my):
          if scrap >= 3:
            scrap -= 3
            fuel += 1
        elif btn_upgrade_reactor.collidepoint(mx, my):
          if scrap >= 15:
            scrap -= 15
            reactor.total_power += 1
            reactor.available_power += 1
        elif btn_leave_shop.collidepoint(mx, my):
          current_state = STATE_MAP
          btn_buy_crew = pygame.Rect(200, 235, 500, 40)
          btn_buy_weapon = pygame.Rect(200, 290, 500, 40)
        elif btn_buy_crew.collidepoint(mx, my):
          if scrap >= 25:
            scrap -= 25
            crew_members.append(Crew(280, 245)) # Spawnt neues Mitglied auf der Brücke
        elif btn_buy_weapon.collidepoint(mx, my):
          if scrap >= 45:
            scrap -= 45
            player_weapons.append(Weapon(charge_time=2.0)) # Zweite, schnellere Waffe

      elif current_state == STATE_EVENT:
        if event_mgr.current_event_type == "COMBAT":
          enemy_hp = 10
          for er in enemy_rooms:
            er.health = 100.0
            er.current_power = 1
          current_state = STATE_COMBAT
        else:
          current_state = STATE_MAP

      elif current_state == STATE_COMBAT:
        if is_targeting:
          # Ziel auswählen und schießen
          for e_room in current_enemy.rooms:
            if e_room.rect.collidepoint(mx, my):
              projectiles.append(
                  Projectile(targeting_start_pos, (mx, my), e_room, True)
              )
              # Finde die erste bereite Waffe und setze sie nach dem Schuss zurück
              for w in player_weapons:
                  if w.is_ready():
                      w.reset()
                      break
              is_targeting = False
              break
          is_targeting = False # Abbrechen, wenn ins Leere geklickt wird
        else:
          # Waffe auswählen, um Zielmodus zu starten
          w_room = PLAYER_SHIP.rooms[1]
          if w_room.rect.collidepoint(mx, my):
            # Prüfen, ob IRGENDEINE Waffe in der Liste bereit ist
            if any(w.is_ready() for w in player_weapons):
              is_targeting = True
              targeting_start_pos = w_room.rect.center

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
          for room in PLAYER_SHIP.rooms:  # <-- Hier anpassen
            if room.rect.collidepoint(mx, my):
              if has_selected:
                for c in crew_members:
                  if c.selected:
                    c.target_pos = (mx, my)
              else:
                room.add_power(reactor)

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
        for room in PLAYER_SHIP.rooms:  # <-- Hier anpassen
          if room.rect.collidepoint(mx, my):
            room.remove_power(reactor)

  # --- LOGIK UPDATES ---
  if not paused and current_state == STATE_COMBAT:
    combat_msg_timer = max(0.0, combat_msg_timer - dt)

    for c in crew_members:
      c.update(dt, player_rooms)

    player_shield.update(dt, player_rooms[0].current_power)
    enemy_shield.update(dt, enemy_rooms[0].current_power)

    # Waffen-Aufladung prüfen (nur aktiv bei funktionierendem Raum)
    for w in player_weapons:
      # Nur prüfen, ob Strom vorhanden ist
      w.update(dt, PLAYER_SHIP.rooms[1].current_power > 0)
      enemy_weapon.update(
          dt, enemy_rooms[1].current_power > 0 and enemy_rooms[1].health > 20.0
      )

    if enemy_weapon.is_ready():
      target_room = random.choice(player_rooms)
      projectiles.append(
          Projectile(
              (enemy_rooms[1].rect.centerx, enemy_rooms[1].rect.centery),
              (target_room.rect.centerx, target_room.rect.centery),
              target_room=target_room,
              is_player_shot=False,
          )
      )
      enemy_weapon.reset()

    for p in projectiles[:]:
      p.update(dt)
      if not p.alive:
        if p.is_player_shot:
          # Ausweichberechnung Gegner
          enemy_evade = enemy_rooms[2].current_power * 0.15
          if random.random() < enemy_evade:
            combat_msg = "FEIND IST AUSGEWICHEN!"
            combat_msg_timer = 1.5
          elif not enemy_shield.attempt_block():
            enemy_hp = max(0, enemy_hp - 1)
            p.target_room.apply_damage(35.0, reactor)
        else:
          # Ausweichberechnung Spieler
          player_evade = player_rooms[2].current_power * 0.20
          if random.random() < player_evade:
            combat_msg = "AUSGEWICHEN!"
            combat_msg_timer = 1.5
          elif not player_shield.attempt_block():
            player_hp = max(0, player_hp - 1)
            p.target_room.apply_damage(35.0, reactor)

        projectiles.remove(p)

    if enemy_hp <= 0:
      scrap += 15
      current_state = STATE_MAP

  # --- RENDERING ---
  screen.fill(COLOR_BG)
  font = pygame.font.SysFont(None, 24)

  screen.blit(
      font.render(
          f"Treibstoff: {fuel}  |  Scrap: {scrap}  |  Hülle:"
          f" {player_hp}/{player_max_hp}",
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
        font.render(
            event_mgr.current_event_text, True, (240, 240, 240)
        ),
        (180, 200),
    )
    screen.blit(
        font.render("[ Klick zum Fortfahren ]", True, COLOR_SELECTED), (340, 330)
    )

  elif current_state == STATE_SHOP:
    pygame.draw.rect(screen, (25, 30, 40), (150, 80, 600, 380))
    pygame.draw.rect(screen, COLOR_SHOP_NODE, (150, 80, 600, 380), 3)

    screen.blit(
        font.render("--- HÄNDLER-STATION ---", True, COLOR_SHOP_NODE), (340, 110)
    )

    pygame.draw.rect(screen, (40, 50, 70), btn_repair)
    pygame.draw.rect(screen, COLOR_BORDER, btn_repair, 2)
    screen.blit(
        font.render(
            "Hülle reparieren (+1 HP) - Kosten: 2 Scrap", True, (220, 220, 220)
        ),
        (btn_repair.x + 20, btn_repair.y + 12),
    )

    pygame.draw.rect(screen, (40, 50, 70), btn_upgrade_reactor)
    pygame.draw.rect(screen, COLOR_BORDER, btn_upgrade_reactor, 2)
    screen.blit(
        font.render(
            "Reaktor aufrüsten (+1 Power) - Kosten: 15 Scrap",
            True,
            (220, 220, 220),
        ),
        (btn_upgrade_reactor.x + 20, btn_upgrade_reactor.y + 12),
    )

    pygame.draw.rect(screen, (60, 40, 40), btn_leave_shop)
    pygame.draw.rect(screen, COLOR_ENEMY_BORDER, btn_leave_shop, 2)
    screen.blit(
        font.render("Shop verlassen", True, (255, 200, 200)),
        (btn_leave_shop.x + 180, btn_leave_shop.y + 12),
    )

  elif current_state == STATE_COMBAT:
    reactor.draw(screen, 30, 45)
    
    # NEU: Zeichne das neue Spieler-Schiff und das aktuelle Gegner-Schiff
    for r in PLAYER_SHIP.rooms:
      r.draw(screen)
    for r in current_enemy.rooms:
      r.draw(screen)
      
    for c in crew_members:
      c.draw(screen)
    for p in projectiles:
      p.draw(screen)

    screen.blit(
        font.render(
            f"Spieler Hülle: {player_hp}/{player_max_hp} HP",
            True,
            (100, 255, 100),
        ),
        (60, 170),
    )
    screen.blit(
        font.render(f"Gegner Hülle: {enemy_hp} HP", True, (255, 100, 100)),
        (550, 170),
    )

    if combat_msg_timer > 0.0:
      msg_txt = font.render(combat_msg, True, COLOR_SELECTED)
      screen.blit(msg_txt, (SCREEN_WIDTH // 2 - 80, 150))
      
    # NEU: Ziel-Linie zeichnen, wenn die Waffe bereit ist und gezielt wird
    if is_targeting:
      mx, my = pygame.mouse.get_pos()
      pygame.draw.line(screen, COLOR_PROJECTILE, targeting_start_pos, (mx, my), 2)
      pygame.draw.circle(screen, COLOR_PROJECTILE, (mx, my), 5, 1)

  pygame.display.flip()

pygame.quit()
sys.exit()