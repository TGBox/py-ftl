import random
import pygame

from classes.Node import *
from settings import *


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