from enums import EventType


class Node:

  def __init__(self, node_id: int, x: int, y: int, event_type: EventType | str) -> None:
    self.id: int = node_id
    self.x: int = x
    self.y: int = y
    self.event_type: EventType | str = event_type  # EventType Enum or str
    self.connections: list[Node] = []
    self.visited: bool = False
    self.hazard_type: str = "NONE"  # 'NONE', 'SOLAR_FLARE', 'ASTEROID_FIELD'

  def __str__(self) -> str:
    """Methode um aus einem Node Objekt einen wohlgeformten String zu generieren, der von Menschen einfach gelesen werden kann.

    Returns:
        str: Der String der die Node repräsentiert.
    """
    n_str = f"Node #{self.id} an Position x={self.x}, y={self.y}. Eventtyp: {self.event_type}, Gefahrentyp: {self.hazard_type}, Bereits besucht: {self.visited}"
    n_str += f"Node hat {len(self.connections)} Verbindungen zu folgenden anderen Nodes: "
    for i, n in enumerate(self.connections):
      n_str += f"{n.id}"
      if i != len(self.connections) - 1:
        n_str += ", "
    return n_str