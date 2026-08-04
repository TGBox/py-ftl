import math
import random
import pygame

from settings import *

import copy

class Weapon:

  def __init__(
      self,
      name: str,
      charge_time: float,
      w_type: str = "LASER",
      ammo_cost: int = 0,
      shield_pierce: int = 0,
      damage: float = 35.0,
  ) -> None:
    self.name: str = name
    self.charge_time: float = charge_time
    self.current_charge: float = 0.0
    self.w_type: str = w_type  # "LASER", "MISSILE", "BEAM"
    self.ammo_cost: int = ammo_cost
    self.shield_pierce: int = shield_pierce
    self.damage: float = damage

  def update(self, dt: float, powered: bool) -> None:
    if powered:
      self.current_charge = min(self.charge_time, self.current_charge + dt)

  def is_ready(self) -> bool:
    return self.current_charge >= self.charge_time

  def reset(self) -> None:
    self.current_charge = 0.0

class StarMap:

  def __init__(self) -> None:
    self.nodes: list[Node] = []
    self.current_node: Node | None = None
    self.sector: int = 1
    self.generate_map()

  def generate_map(self) -> None:
    self.nodes.clear()
    node_id = 0
    num_layers = 7  # Größere Karte (7 Ebenen)
    layer_distance = 110
    created_layers: list[list[Node]] = []

    # Start-Knoten
    start_node = Node(node_id, 80, 275, "EMPTY")
    self.nodes.append(start_node)
    created_layers.append([start_node])
    node_id += 1

    # Mittlere Ebenen
    for l in range(1, num_layers - 1):
      layer_nodes: list[Node] = []
      node_count = random.randint(2, 3)
      x = 80 + l * layer_distance
      y_positions = (
          [275]
          if node_count == 1
          else (
              [180, 370] if node_count == 2 else [130, 275, 420]
          )
      )

      for y in y_positions:
        event_type = random.choice(
            ["COMBAT", "COMBAT", "RESOURCE", "SHOP", "EMPTY"]
        )
        node = Node(node_id, x, y, event_type)
        self.nodes.append(node)
        layer_nodes.append(node)
        node_id += 1
      created_layers.append(layer_nodes)

    # Exit-Knoten (Ziel)
    exit_node = Node(node_id, 80 + (num_layers - 1) * layer_distance, 275, "EXIT")
    self.nodes.append(exit_node)
    created_layers.append([exit_node])

    # Wege zwischen den Ebenen verbinden
    for i in range(len(created_layers) - 1):
      for n1 in created_layers[i]:
        # Verbinde mit mindestens einem Knoten der nächsten Ebene
        targets = random.sample(
            created_layers[i + 1],
            k=min(len(created_layers[i + 1]), random.randint(1, 2)),
        )
        for t in targets:
          if t not in n1.connections:
            n1.connections.append(t)

    self.current_node = start_node
    self.current_node.visited = True

  def draw(self, surface: pygame.Surface) -> None:
    # Linien zeichnen
    for node in self.nodes:
      for conn in node.connections:
        pygame.draw.line(
            surface, COLOR_MAP_LINE, (node.x, node.y), (conn.x, conn.y), 2
        )

    # Knoten zeichnen
    for node in self.nodes:
      if node == self.current_node:
        color = COLOR_SELECTED
      elif node.event_type == "EXIT":
        color = (255, 100, 255)
      elif node.event_type == "SHOP" and not node.visited:
        color = COLOR_SHOP_NODE
      elif node.visited:
        color = (100, 255, 100)
      else:
        color = COLOR_MAP_NODE

      pygame.draw.circle(surface, color, (node.x, node.y), 14)

      if (
          self.current_node is not None
          and node in self.current_node.connections
      ):
        pygame.draw.circle(surface, (255, 255, 255), (node.x, node.y), 18, 2)

class Room:

  def __init__(
      self,
      name: str,
      rect: tuple[int, int, int, int],
      max_power: int = 3,
      is_enemy: bool = False,
  ) -> None:
    self.name: str = name
    self.rect: pygame.Rect = pygame.Rect(rect)
    self.max_power: int = max_power
    self.current_power: int = 0
    self.is_enemy: bool = is_enemy
    self.health: float = 100.0
    self.max_health: float = 100.0

  def effective_max_power(self) -> int:
    return max(0, math.floor(self.max_power * (self.health / self.max_health)))

  def add_power(self, reactor: Reactor) -> None:
    if (
        self.current_power < self.effective_max_power()
        and reactor.available_power > 0
    ):
      self.current_power += 1
      reactor.available_power -= 1

  def remove_power(self, reactor: Reactor) -> None:
    if self.current_power > 0:
      self.current_power -= 1
      reactor.available_power += 1

  def apply_damage(self, amount: float, reactor: Reactor) -> None:
    self.health = max(0.0, self.health - amount)
    while self.current_power > self.effective_max_power():
      self.remove_power(reactor)

  def repair(self, amount: float) -> None:
    self.health = min(self.max_health, self.health + amount)

  def draw(self, surface: pygame.Surface) -> None:
    fill_col = COLOR_ENEMY_ROOM if self.is_enemy else COLOR_ROOM
    border_col = COLOR_ENEMY_BORDER if self.is_enemy else COLOR_BORDER
    pygame.draw.rect(surface, fill_col, self.rect)
    pygame.draw.rect(surface, border_col, self.rect, 2)

    font = pygame.font.SysFont(None, 20)
    surface.blit(
        font.render(self.name, True, (220, 220, 220)),
        (self.rect.x + 6, self.rect.y + 6),
    )

    # System-Gesundheitsbalken
    hp_ratio = self.health / self.max_health
    hp_color = COLOR_HP_GREEN if hp_ratio > 0.4 else COLOR_HP_RED
    pygame.draw.rect(
        surface,
        (30, 30, 30),
        (self.rect.x + 6, self.rect.y + 24, self.rect.width - 12, 5),
    )
    pygame.draw.rect(
        surface,
        hp_color,
        (
            self.rect.x + 6,
            self.rect.y + 24,
            int((self.rect.width - 12) * hp_ratio),
            5,
        ),
    )

    if not self.is_enemy:
      eff_max = self.effective_max_power()
      for i in range(self.max_power):
        if i < eff_max:
          color = (
              COLOR_POWER_ACTIVE
              if i < self.current_power
              else COLOR_POWER_OFF
          )
        else:
          color = COLOR_HP_RED
        pygame.draw.rect(
            surface,
            color,
            (self.rect.x + 6 + (i * 14), self.rect.bottom - 20, 10, 12),
        )

class ShipModel:
    def __init__(self, name: str, max_hp: int, rooms: list[Room], is_enemy: bool = False):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.rooms = rooms
        self.is_enemy = is_enemy
        

PLAYER_SHIP = ShipModel("Kestrel", 15, [
    Room("Schild", (60, 200, 90, 90)),
    Room("Waffen", (160, 200, 90, 90)),
    Room("Brücke", (260, 200, 90, 90), max_power=2)
])

ENEMY_SCOUT = ShipModel("Scout", 8, [
    Room("Schild", (600, 200, 80, 80), is_enemy=True),
    Room("Waffen", (690, 200, 80, 80), is_enemy=True),
    Room("Brücke", (780, 200, 80, 80), is_enemy=True)
], is_enemy=True)

ENEMY_BOSS = ShipModel("Flaggschiff", 25, [
    Room("Schild", (550, 150, 100, 100), is_enemy=True),
    Room("Laser", (670, 100, 80, 80), is_enemy=True),
    Room("Raketen", (670, 200, 80, 80), is_enemy=True),
    Room("Brücke", (770, 150, 100, 100), is_enemy=True)
], is_enemy=True)

# Standardgegner für den Start festlegen
current_enemy: ShipModel = copy.deepcopy(ENEMY_SCOUT)

class ShieldSystem:

  def __init__(self, recharge_time: float = 4.0) -> None:
    self.max_layers: int = 0
    self.current_layers: int = 0
    self.recharge_timer: float = 0.0
    self.recharge_time: float = recharge_time

  def update(self, dt: float, powered_layers: int) -> None:
    self.max_layers = powered_layers
    if self.current_layers > self.max_layers:
      self.current_layers = self.max_layers

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
      self.recharge_timer = 0.0
      return True
    return False

  def draw_bubble(
      self, surface: pygame.Surface, center: tuple[int, int], base_radius: int
  ) -> None:
    for i in range(self.current_layers):
      radius = base_radius + (i * 12)
      pygame.draw.circle(surface, (80, 150, 255), center, radius, 3)
    
class Projectile:

  def __init__(
      self,
      start_pos: tuple[int, int],
      target_pos: tuple[int, int],
      target_room: Room,
      is_player_shot: bool,
      w_type: str = "LASER",
      shield_pierce: int = 0,
      damage: float = 35.0,
  ) -> None:
    self.x: float = float(start_pos[0])
    self.y: float = float(start_pos[1])
    self.target_x: float = float(target_pos[0])
    self.target_y: float = float(target_pos[1])
    self.target_room: Room = target_room
    self.is_player_shot: bool = is_player_shot
    self.w_type: str = w_type
    self.shield_pierce: int = shield_pierce
    self.damage: float = damage
    self.alive: bool = True

    dx = self.target_x - self.x
    dy = self.target_y - self.y
    dist = math.hypot(dx, dy)
    speed = 600.0 if w_type == "BEAM" else 400.0
    self.vx: float = (dx / dist) * speed if dist != 0 else 0.0
    self.vy: float = (dy / dist) * speed if dist != 0 else 0.0

  def update(self, dt: float) -> None:
    self.x += self.vx * dt
    self.y += self.vy * dt
    if math.hypot(self.target_x - self.x, self.target_y - self.y) < 10:
      self.alive = False

  def draw(self, surface: pygame.Surface) -> None:
    if self.w_type == "MISSILE":
      pygame.draw.rect(
          surface, (255, 140, 0), (int(self.x) - 4, int(self.y) - 4, 8, 8)
      )
    elif self.w_type == "BEAM":
      pygame.draw.circle(
          surface, (255, 255, 100), (int(self.x), int(self.y)), 7
      )
    else:  # LASER
      pygame.draw.circle(
          surface, COLOR_PROJECTILE, (int(self.x), int(self.y)), 5
      )

class Node:

  def __init__(self, node_id: int, x: int, y: int, event_type: str) -> None:
    self.id: int = node_id
    self.x: int = x
    self.y: int = y
    self.event_type: str = event_type  # 'COMBAT', 'RESOURCE', 'SHOP', 'EMPTY', 'EXIT'
    self.connections: list[Node] = []
    self.visited: bool = False

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

class EventManager:

  def __init__(self) -> None:
    self.current_event_text: str = ""
    self.current_event_type: str | None = None

  def trigger_event(self, event_type: str) -> tuple[int, int]:
    self.current_event_type = event_type
    if event_type == "RESOURCE":
      scrap_found = random.randint(10, 25)
      fuel_found = random.randint(1, 2)
      self.current_event_text = (
          f"Wrack untersucht! Fund: {scrap_found} Scrap, {fuel_found}"
          " Treibstoff."
      )
      return scrap_found, fuel_found
    elif event_type == "COMBAT":
      self.current_event_text = (
          "WARNUNG! Ein feindliches Piratenschiff greift an!"
      )
      return 0, 0
    elif event_type == "SHOP":
      self.current_event_text = (
          "Willkommen an der Händler-Station! Bereit zum Handeln."
      )
      return 0, 0
    else:
      self.current_event_text = (
          "Dieser Sektor ist ruhig. Keine Aktivitäten gemeldet."
      )
      return 0, 0
  
class Reactor:

  def __init__(self, total_power: int = 6) -> None:
    self.total_power: int = total_power
    self.available_power: int = total_power

  def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
    font = pygame.font.SysFont(None, 22)
    surface.blit(
        font.render(
            f"Reaktor: {self.available_power}/{self.total_power}",
            True,
            (200, 220, 255),
        ),
        (x, y),
    )
    for i in range(self.total_power):
      color = COLOR_REACTOR if i < self.available_power else COLOR_POWER_OFF
      pygame.draw.rect(surface, color, (x + i * 18, y + 25, 14, 25))
      
