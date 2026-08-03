import sys
import math
import random
import pygame

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 550
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FTL Prototype - Sternenkarte & Events")
clock = pygame.time.Clock()

# Farben
COLOR_BG = (15, 18, 24)
COLOR_ROOM = (40, 50, 70)
COLOR_ENEMY_ROOM = (70, 40, 50)
COLOR_BORDER = (100, 140, 180)
COLOR_ENEMY_BORDER = (180, 100, 100)
COLOR_CREW = (50, 200, 100)
COLOR_SELECTED = (255, 200, 0)
COLOR_POWER_ACTIVE = (0, 220, 120)
COLOR_POWER_OFF = (60, 70, 80)
COLOR_REACTOR = (0, 180, 255)
COLOR_WEAPON_CHARGE = (255, 180, 0)
COLOR_PROJECTILE = (255, 50, 50)
COLOR_SHIELD = (100, 200, 255)
COLOR_MAP_NODE = (150, 180, 220)
COLOR_MAP_LINE = (50, 70, 100)

# Zustände
STATE_MAP = "MAP"
STATE_EVENT = "EVENT"
STATE_COMBAT = "COMBAT"
current_state = STATE_MAP


# --- STERNENKARTE & EVENTS ---
class Node:

  def __init__(self, node_id, x, y, event_type):
    self.id = node_id
    self.x = x
    self.y = y
    self.event_type = event_type  # 'COMBAT', 'RESOURCE', 'EMPTY'
    self.connections = []
    self.visited = False


class StarMap:

  def __init__(self):
    self.nodes = []
    self.current_node = None
    self.generate_map()

  def generate_map(self):
    # Einfache ebenenbasierte Kartengenerierung (4 Ebenen)
    layers = [[(100, 275)], [(300, 150), (300, 400)], [(500, 200), (500, 350)], [(750, 275)]]
    node_id = 0

    created_layers = []
    for layer in layers:
      layer_nodes = []
      for x, y in layer:
        event_type = random.choice(['COMBAT', 'RESOURCE', 'EMPTY'])
        node = Node(node_id, x, y, event_type)
        self.nodes.append(node)
        layer_nodes.append(node)
        node_id += 1
      created_layers.append(layer_nodes)

    # Verbindungen herstellen
    for i in range(len(created_layers) - 1):
      for n1 in created_layers[i]:
        for n2 in created_layers[i + 1]:
          n1.connections.append(n2)

    self.current_node = self.nodes[0]
    self.current_node.visited = True
    self.current_node.event_type = 'EMPTY'

  def draw(self, surface):
    # Linien zeichnen
    for node in self.nodes:
      for conn in node.connections:
        pygame.draw.line(surface, COLOR_MAP_LINE, (node.x, node.y), (conn.x, conn.y), 2)

    # Nodes zeichnen
    for node in self.nodes:
      color = COLOR_SELECTED if node == self.current_node else (
          (100, 255, 100) if node.visited else COLOR_MAP_NODE
      )
      pygame.draw.circle(surface, color, (node.x, node.y), 16)

      # Markierung erreichbarer Nodes
      if node in self.current_node.connections:
        pygame.draw.circle(surface, (255, 255, 255), (node.x, node.y), 20, 2)


# --- EVENT SYSTEM ---
class EventManager:

  def __init__(self):
    self.current_event_text = ""
    self.current_event_type = None

  def trigger_event(self, event_type):
    self.current_event_type = event_type
    if event_type == "RESOURCE":
      scrap = random.randint(10, 25)
      fuel = random.randint(1, 2)
      self.current_event_text = f"Schiffs-Wrack untersucht! Fund: {scrap} Scrap, {fuel} Treibstoff."
      return scrap, fuel
    elif event_type == "COMBAT":
      self.current_event_text = "WARNUNG! Ein feindliches Piratenschiff greift an!"
      return 0, 0
    else:
      self.current_event_text = "Dieser Sektor ist ruhig. Keine Aktivitäten gemeldet."
      return 0, 0


# --- SPIELKLASSEN (aus vorherigen Iterationen) ---
class Reactor:

  def __init__(self, total_power=6):
    self.total_power = total_power
    self.available_power = total_power

  def draw(self, surface, x, y):
    font = pygame.font.SysFont(None, 22)
    surface.blit(
        font.render(f"Reaktor: {self.available_power}/{self.total_power}", True, (200, 220, 255)),
        (x, y),
    )
    for i in range(self.total_power):
      color = COLOR_REACTOR if i < self.available_power else COLOR_POWER_OFF
      pygame.draw.rect(surface, color, (x + i * 18, y + 25, 14, 25))


class Room:

  def __init__(self, name, rect, max_power=3, is_enemy=False):
    self.name = name
    self.rect = pygame.Rect(rect)
    self.max_power = max_power
    self.current_power = 0
    self.is_enemy = is_enemy

  def add_power(self, reactor):
    if self.current_power < self.max_power and reactor.available_power > 0:
      self.current_power += 1
      reactor.available_power -= 1

  def remove_power(self, reactor):
    if self.current_power > 0:
      self.current_power -= 1
      reactor.available_power += 1

  def draw(self, surface):
    fill_col = COLOR_ENEMY_ROOM if self.is_enemy else COLOR_ROOM
    border_col = COLOR_ENEMY_BORDER if self.is_enemy else COLOR_BORDER
    pygame.draw.rect(surface, fill_col, self.rect)
    pygame.draw.rect(surface, border_col, self.rect, 2)
    font = pygame.font.SysFont(None, 20)
    surface.blit(font.render(self.name, True, (220, 220, 220)), (self.rect.x + 6, self.rect.y + 6))
    if not self.is_enemy:
      for i in range(self.max_power):
        color = COLOR_POWER_ACTIVE if i < self.current_power else COLOR_POWER_OFF
        pygame.draw.rect(
            surface, color, (self.rect.x + 6 + (i * 14), self.rect.bottom - 20, 10, 12)
        )


class Weapon:

  def __init__(self, charge_time=3.0):
    self.charge_time = charge_time
    self.current_charge = 0.0

  def update(self, dt, powered):
    if powered:
      self.current_charge = min(self.charge_time, self.current_charge + dt)

  def is_ready(self):
    return self.current_charge >= self.charge_time

  def reset(self):
    self.current_charge = 0.0


class ShieldSystem:

  def __init__(self):
    self.current_layers = 0

  def update(self, powered_layers):
    self.current_layers = powered_layers

  def attempt_block(self):
    if self.current_layers > 0:
      self.current_layers -= 1
      return True
    return False


class Projectile:

  def __init__(self, start_pos, target_pos, is_player_shot):
    self.x, self.y = start_pos
    self.target_x, self.target_y = target_pos
    self.is_player_shot = is_player_shot
    self.alive = True
    dx, dy = self.target_x - self.x, self.target_y - self.y
    dist = math.hypot(dx, dy)
    self.vx = (dx / dist) * 400.0 if dist != 0 else 0
    self.vy = (dy / dist) * 400.0 if dist != 0 else 0

  def update(self, dt):
    self.x += self.vx * dt
    self.y += self.vy * dt
    if math.hypot(self.target_x - self.x, self.target_y - self.y) < 10:
      self.alive = False

  def draw(self, surface):
    pygame.draw.circle(surface, COLOR_PROJECTILE, (int(self.x), int(self.y)), 5)


class Crew:

  def __init__(self, x, y):
    self.x, self.y = x, y
    self.radius = 12
    self.selected = False
    self.target_pos = None

  def update(self, dt):
    if self.target_pos:
      tx, ty = self.target_pos
      dx, dy = tx - self.x, ty - self.y
      dist = math.hypot(dx, dy)
      if dist < 120.0 * dt:
        self.x, self.y = tx, ty
        self.target_pos = None
      else:
        self.x += (dx / dist) * 120.0 * dt
        self.y += (dy / dist) * 120.0 * dt

  def draw(self, surface):
    color = COLOR_SELECTED if self.selected else COLOR_CREW
    pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)


# --- SETUP ---
star_map = StarMap()
event_mgr = EventManager()

fuel = 5
scrap = 10

reactor = Reactor(total_power=6)
player_rooms = [
    Room("Schild", (60, 200, 110, 90)),
    Room("Waffen", (180, 200, 110, 90)),
    Room("Brücke", (300, 200, 90, 90)),
]
enemy_rooms = [
    Room("Schild", (550, 200, 110, 90), is_enemy=True),
    Room("Waffen", (670, 200, 110, 90), is_enemy=True),
    Room("Brücke", (790, 200, 80, 90), is_enemy=True),
]

player_shield = ShieldSystem()
enemy_shield = ShieldSystem()
crew_members = [Crew(340, 245), Crew(115, 245)]
player_weapon = Weapon(charge_time=3.0)
enemy_weapon = Weapon(charge_time=5.0)

projectiles = []
player_hp, enemy_hp = 10, 10
paused = False
running = True

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

      # KARTEN-STEUERUNG
      if current_state == STATE_MAP:
        for node in star_map.current_node.connections:
          if math.hypot(mx - node.x, my - node.y) <= 20 and fuel > 0:
            fuel -= 1
            star_map.current_node = node
            node.visited = True
            add_scrap, add_fuel = event_mgr.trigger_event(node.event_type)
            scrap += add_scrap
            fuel += add_fuel

            if node.event_type == "COMBAT":
              enemy_hp = 10
              current_state = STATE_EVENT
            else:
              current_state = STATE_EVENT
            break

      # EVENT-STEUERUNG
      elif current_state == STATE_EVENT:
        if event_mgr.current_event_type == "COMBAT":
          current_state = STATE_COMBAT
        else:
          current_state = STATE_MAP

      # KAMPF-STEUERUNG
      elif current_state == STATE_COMBAT:
        if player_weapon.is_ready():
          for e_room in enemy_rooms:
            if e_room.rect.collidepoint(mx, my):
              w_room = player_rooms[1]
              projectiles.append(
                  Projectile(
                      (w_room.rect.centerx, w_room.rect.centery), (mx, my), is_player_shot=True
                  )
              )
              player_weapon.reset()
              break

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
          for room in player_rooms:
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
        for room in player_rooms:
          if room.rect.collidepoint(mx, my):
            room.remove_power(reactor)

  # --- LOGIK UPDATES ---
  if not paused and current_state == STATE_COMBAT:
    for c in crew_members:
      c.update(dt)

    player_shield.update(player_rooms[0].current_power)
    enemy_shield.update(1)

    player_weapon.update(dt, player_rooms[1].current_power > 0)
    enemy_weapon.update(dt, True)

    if enemy_weapon.is_ready():
      target = player_rooms[0]
      projectiles.append(
          Projectile(
              (enemy_rooms[1].rect.centerx, enemy_rooms[1].rect.centery),
              (target.rect.centerx, target.rect.centery),
              is_player_shot=False,
          )
      )
      enemy_weapon.reset()

    for p in projectiles[:]:
      p.update(dt)
      if not p.alive:
        if p.is_player_shot:
          if not enemy_shield.attempt_block():
            enemy_hp = max(0, enemy_hp - 1)
        else:
          if not player_shield.attempt_block():
            player_hp = max(0, player_hp - 1)
        projectiles.remove(p)

    # Sieg im Kampf -> zurück zur Karte
    if enemy_hp <= 0:
      scrap += 15
      current_state = STATE_MAP

  # --- RENDERING ---
  screen.fill(COLOR_BG)
  font = pygame.font.SysFont(None, 24)

  # HUD (Ressourcen)
  screen.blit(
      font.render(f"Treibstoff: {fuel}  |  Scrap: {scrap}", True, (255, 255, 255)), (30, 15)
  )

  if current_state == STATE_MAP:
    star_map.draw(screen)
    screen.blit(
        font.render(
            "STERNENKARTE: Klicke auf eine weiß umrandete Node zum Reisen", True, (200, 200, 200)
        ),
        (200, 500),
    )

  elif current_state == STATE_EVENT:
    pygame.draw.rect(screen, (30, 40, 55), (150, 150, 600, 250))
    pygame.draw.rect(screen, COLOR_BORDER, (150, 150, 600, 250), 3)

    event_txt = font.render(event_mgr.current_event_text, True, (240, 240, 240))
    screen.blit(event_txt, (180, 200))

    btn_txt = font.render("[ Klick zum Fortfahren ]", True, COLOR_SELECTED)
    screen.blit(btn_txt, (340, 330))

  elif current_state == STATE_COMBAT:
    reactor.draw(screen, 30, 45)
    for r in player_rooms:
      r.draw(screen)
    for r in enemy_rooms:
      r.draw(screen)
    for c in crew_members:
      c.draw(screen)
    for p in projectiles:
      p.draw(screen)

    screen.blit(
        font.render(f"Spieler Hülle: {player_hp} HP", True, (100, 255, 100)), (60, 170)
    )
    screen.blit(
        font.render(f"Gegner Hülle: {enemy_hp} HP", True, (255, 100, 100)), (550, 170)
    )

  pygame.display.flip()

pygame.quit()
sys.exit()