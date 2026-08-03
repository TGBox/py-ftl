class Node:

  def __init__(self, node_id: int, x: int, y: int, event_type: str) -> None:
    self.id: int = node_id
    self.x: int = x
    self.y: int = y
    self.event_type: str = event_type  # 'COMBAT', 'RESOURCE', 'SHOP', 'EMPTY', 'EXIT'
    self.connections: list[Node] = []
    self.visited: bool = False
