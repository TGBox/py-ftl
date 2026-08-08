import random
import pygame

from classes.Node import *
from settings import *


class StarMap:

  def __init__(self) -> None:
    self.nodes: list[Node] = []
    self.current_node: Node | None = None
    self.sector: int = 1
    self.rebel_fleet_x: float = 30.0
    self.sector_type: str = "Zivil"
    self.generate_map()

  def advance_fleet(self) -> None:
    self.rebel_fleet_x += REBEL_FLEET_SPEED

  def generate_map(self) -> None:
    self.nodes.clear()
    self.rebel_fleet_x = 30.0

    sector_choices = ["Zivil-Sektor", "Rebellen-Sektor", "Nebel-Sektor", "Mantis-Jagdgebiet", "Kristall-Sektor"]
    self.sector_type = sector_choices[(self.sector - 1) % len(sector_choices)]

    node_id = 0
    num_layers = 7  
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
          [275] if node_count == 1 else ([180, 370] if node_count == 2 else [130, 275, 420])
      )

      for y in y_positions:
        event_type = random.choice(["COMBAT", "RESOURCE", "DISTRESS", "NEBULA", "SHOP", "TRAINING", "EMPTY"])
        node = Node(node_id, x, y, event_type)
        self.nodes.append(node)
        layer_nodes.append(node)
        node_id += 1
      created_layers.append(layer_nodes)

    # Exit-Knoten (Ziel)
    exit_node = Node(node_id, 80 + (num_layers - 1) * layer_distance, 275, "EXIT")
    self.nodes.append(exit_node)
    created_layers.append([exit_node])

    # Saubere Verbindung der Ebenen
    for i in range(len(created_layers) - 1):
      for n1 in created_layers[i]:
        next_layer = created_layers[i + 1]
        targets = random.sample(next_layer, k=min(len(next_layer), random.randint(1, 2)))
        for t in targets:
          if t not in n1.connections:
            n1.connections.append(t)
          if n1 not in t.connections:
            t.connections.append(n1)

    for i in range(len(created_layers) - 1):
      for n2 in created_layers[i + 1]:
        has_incoming = any(n2 in n1.connections for n1 in created_layers[i])
        if not has_incoming:
          src = random.choice(created_layers[i])
          src.connections.append(n2)
          n2.connections.append(src)

    self.current_node = start_node
    self.current_node.visited = True

    # Umweltgefahren auf 30% der Knoten verteilen (mindestens 2 Knoten garantiert)
    hazard_types = ["SOLAR_FLARE", "ASTEROID_FIELD", "NEBULA_ION_STORM", "PULSAR"]
    eligible = [n for n in self.nodes if n.event_type in ("COMBAT", "EMPTY", "RESOURCE", "NEBULA")]
    if eligible:
        guaranteed = random.sample(eligible, k=min(2, len(eligible)))
        for n in guaranteed:
            n.hazard_type = random.choice(hazard_types)
        for node in eligible:
            if node not in guaranteed and random.random() < 0.30:
                node.hazard_type = random.choice(hazard_types)


  def draw(self, surface: pygame.Surface) -> None:
    # Linien zeichnen
    for node in self.nodes:
      for conn in node.connections:
        pygame.draw.line(
            surface, COLOR_MAP_LINE, (node.x, node.y), (conn.x, conn.y), 2
        )

    # Rebellenflotte Linie zeichnen
    fleet_x = int(self.rebel_fleet_x)
    if fleet_x > 0:
      # Aktuelle Flottenlinie
      pygame.draw.line(surface, (220, 50, 50), (fleet_x, 60), (fleet_x, 520), 3)
      lbl = get_font(18).render("REBELLENFLOTTE", True, (255, 80, 80))
      surface.blit(lbl, (fleet_x + 5, 70))

      # Vorschau-Linie für nächsten Sprung
      next_fleet_x = int(self.rebel_fleet_x + REBEL_FLEET_SPEED)
      if next_fleet_x < 900:
        for y_dash in range(60, 520, 15):
          pygame.draw.line(surface, (255, 140, 40), (next_fleet_x, y_dash), (next_fleet_x, min(520, y_dash + 8)), 2)
        next_lbl = get_font(14).render("FLOTTE (NÄCHSTER SPRUNG)", True, (255, 160, 60))
        surface.blit(next_lbl, (next_fleet_x + 5, 90))

    # Knoten zeichnen
    for node in self.nodes:
      if node == self.current_node:
        color = COLOR_SELECTED
      elif node.visited:
        color = COLOR_MAP_VISITED
      elif node.event_type == "EXIT":
        color = (255, 100, 255)
      elif node.event_type == "SHOP":
        color = COLOR_SHOP_NODE
      elif node.event_type == "TRAINING":
        color = COLOR_TRAINING_NODE
      else:
        color = COLOR_MAP_NODE

      pygame.draw.circle(surface, color, (node.x, node.y), 14)

      # Umweltgefahr-Ring um Knoten zeichnen
      h_type = getattr(node, "hazard_type", "NONE")
      if h_type == "SOLAR_FLARE":
        pygame.draw.circle(surface, (255, 140, 0), (node.x, node.y), 17, 2)
      elif h_type == "ASTEROID_FIELD":
        pygame.draw.circle(surface, (160, 160, 180), (node.x, node.y), 17, 2)
      elif h_type == "NEBULA_ION_STORM":
        pygame.draw.circle(surface, (0, 220, 255), (node.x, node.y), 17, 2)
      elif h_type == "PULSAR":
        pygame.draw.circle(surface, (255, 230, 80), (node.x, node.y), 17, 2)

      # Subtiler innerer Indikator für besuchte Knoten
      if node.visited and node != self.current_node:
        pygame.draw.circle(surface, (40, 50, 65), (node.x, node.y), 5)

      if (
          self.current_node is not None
          and node in self.current_node.connections
      ):
        pygame.draw.circle(surface, (255, 255, 255), (node.x, node.y), 18, 2)