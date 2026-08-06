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
        self.crew: list[Crew] = [Crew(340, 245, species="Mensch"), Crew(115, 245, species="Engi")]
        self.weapons: list[Weapon] = [
            Weapon("Standard Laser", charge_time=3.0, w_type="LASER"),
            Weapon("Artemis Rakete", charge_time=4.0, w_type="MISSILE", ammo_cost=1),
        ]
        self.projectiles: list[Projectile] = []
        self.scrap: int = PLAYER_START_SCRAP
        self.fuel: int = PLAYER_START_FUEL
        self.missiles: int = PLAYER_START_MISSILES
        self.drone_parts: int = 5
        self.augments: list[str] = ["Waffen-Vorheizer"]
        self.show_crew_menu: bool = False
        self.renaming_crew_idx: Optional[int] = None
        self.active_rename_idx: Optional[int] = None
        self.rename_buffer: str = ""
        from managers.save_manager import SaveManager
        self.unlocked_ships: list[str] = SaveManager.load_unlocks()
        self.newly_unlocked_ship: Optional[str] = None




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
        self.teleport_cooldown: float = 0.0
        self.is_teleport_targeting: bool = False
        self.cloak_active_timer: float = 0.0
        self.cloak_cooldown: float = 0.0
        self.solar_flare_timer: float = 20.0
        self.solar_flare_flash: float = 0.0
        self.asteroid_timer: float = 2.5
        self.combat_drone_active: bool = False
        self.repair_drone_active: bool = False
        self.drone_orbit_angle: float = 0.0
        self.drone_fire_timer: float = 0.0
        self.repair_drone_pos: tuple[float, float] = (160.0, 245.0)


class WorldData:

    def __init__(self) -> None:
        self.star_map: StarMap = StarMap()
        self.event_manager: EventManager = EventManager()


class GameData:

    def __init__(self) -> None:
        self.running: bool = True
        self.paused: bool = False
        self.show_pause_menu: bool = False
        self.current_state: str = STATE_MAIN_MENU

        self.player: PlayerData = PlayerData()
        self.enemy: EnemyData = EnemyData()
        self.combat: CombatData = CombatData()
        self.world: WorldData = WorldData()