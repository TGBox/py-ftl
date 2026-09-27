from enums import EventType, HazardType


class Node:

  def __init__(self, node_id: int, x: int, y: int, event_type: EventType | str) -> None:
    self.id: int = node_id
    self.x: int = x
    self.y: int = y
    self.event_type: EventType | str = event_type  # EventType Enum or str
    self.connections: list[Node] = []
    self.visited: bool = False
    self.hazard_type: HazardType | str = HazardType.NONE

  def __repr__(self) -> str:
    return f"<Node #{self.id} pos=({self.x},{self.y}) type={self.event_type} visited={self.visited}>"