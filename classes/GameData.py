import copy
from typing import Literal, Optional, Tuple

from classes.EventManager import EventManager
from classes.StarMap import StarMap
from classes.Crew import Crew
from classes.Reactor import Reactor
from classes.Projectile import Projectile
from classes.Room import Room
from classes.ShieldSystem import ShieldSystem
from classes.ShipModel import ENEMY_SCOUT, PLAYER_SHIP, ShipModel
from classes.Weapon import Weapon
from settings import *


class GameData:
    
    def __init__(self) -> None:
        self.current_state = STATE_MAP  # <-- Hier ändern!
        self.player_targeting_weapon_idx: Optional[int] = None
        self.player_targeting_start_pos: Tuple[int, int] = (0, 0)
        # Player.
        self.player_ship: ShipModel = copy.deepcopy(PLAYER_SHIP)
        self.player_reactor: Reactor = Reactor(total_power=PLAYER_START_POWER)
        self.player_shield: ShieldSystem = ShieldSystem()
        self.player_projectiles: list[Projectile] = []
        self.player_crew: list[Crew] = [Crew(340, 245), Crew(115, 245)]
        self.player_weapons: list[Weapon] = [
            Weapon("Standard Laser", charge_time=3.0, w_type="LASER"),  #[cite: 13]
            Weapon(
                "Artemis Rakete", charge_time=4.0, w_type="MISSILE", ammo_cost=1
            ),  #[cite: 1, 13]
        ]
        self.player_scrap: int = PLAYER_START_SCRAP
        self.player_fuel: int = PLAYER_START_FUEL
        self.player_missiles: int = PLAYER_START_MISSILES
        self.player_weapon_targets: dict[int, tuple[Room, tuple[Literal[0], Literal[0]] | tuple[int, int], tuple[int, int]]] = {}  # weapon_idx: (target_room, start_pos, end_pos)
        self.is_player_targeting = False
        self.player_targeting_weapon_idx = None
        self.player_targeting_start_pos = (0, 0)
        self.player_autofire_enabled = False
        
        # Enemy.
        self.current_enemy_ship: ShipModel = copy.deepcopy(ENEMY_SCOUT)
        self.enemy_reactor: Reactor = Reactor(total_power=ENEMY_START_POWER)
        self.enemy_shield: ShieldSystem = ShieldSystem()
        self.enemy_weapon: Weapon = Weapon("Laser", charge_time=4.5, w_type="LASER")
        
        # Game.
        self.combat_msg = ""
        self.combat_msg_timer = 0.0
        self.paused = False
        self.running = True
        self.star_map: StarMap = StarMap()
        self.event_manager: EventManager = EventManager()