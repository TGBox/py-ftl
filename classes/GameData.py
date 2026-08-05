import copy
from typing import Optional, Tuple

from classes.Crew import Crew
from classes.EventManager import EventManager
from classes.Projectile import Projectile
from classes.Reactor import Reactor
from classes.Room import Room
from classes.ShieldSystem import ShieldSystem
from classes.ShipModel import ENEMY_SCOUT, PLAYER_SHIP, ShipModel
from classes.StarMap import StarMap
from classes.Weapon import Weapon
from settings import *


class PlayerData:

    def __init__(self) -> None:
        self.ship: ShipModel = copy.deepcopy(PLAYER_SHIP)
        self.reactor: Reactor = Reactor(total_power=PLAYER_START_POWER)
        self.shield: ShieldSystem = ShieldSystem()
        self.crew: list[Crew] = [Crew(340, 245, name="Alpha", species="Mensch"), Crew(115, 245, name="Beta", species="Engi")]
        self.weapons: list[Weapon] = [
            Weapon("Standard Laser", charge_time=3.0, w_type="LASER"),
            Weapon("Artemis Rakete", charge_time=4.0, w_type="MISSILE", ammo_cost=1),
        ]
        self.projectiles: list[Projectile] = []
        self.scrap: int = PLAYER_START_SCRAP
        self.fuel: int = PLAYER_START_FUEL
        self.missiles: int = PLAYER_START_MISSILES


class EnemyData:

    def __init__(self) -> None:
        self.ship: ShipModel = copy.deepcopy(ENEMY_SCOUT)
        self.reactor: Reactor = Reactor(total_power=ENEMY_START_POWER)
        self.shield: ShieldSystem = ShieldSystem()
        self.weapon: Weapon = Weapon("Laser", charge_time=4.5, w_type="LASER")


class CombatData:

    def __init__(self) -> None:
        self.autofire_enabled: bool = False
        self.is_targeting: bool = False
        self.target_weapon_idx: Optional[int] = None
        self.start_pos: Tuple[int, int] = (0, 0)
        self.weapon_targets: dict[int, tuple[Room, tuple[int, int], tuple[int, int]]] = {}
        self.msg: str = ""
        self.msg_timer: float = 0.0


class WorldData:

    def __init__(self) -> None:
        self.star_map: StarMap = StarMap()
        self.event_manager: EventManager = EventManager()


class GameData:

    def __init__(self) -> None:
        self.running: bool = True
        self.paused: bool = False
        self.current_state: str = STATE_MAIN_MENU

        self.player: PlayerData = PlayerData()
        self.enemy: EnemyData = EnemyData()
        self.combat: CombatData = CombatData()
        self.world: WorldData = WorldData()