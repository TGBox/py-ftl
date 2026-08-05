import copy

from classes.Node import Node
from classes.GameData import GameData
from classes.ShipModel import ENEMY_BOSS, ENEMY_SCOUT
from settings import *


class MapManager:

    def __init__(self, data: GameData):
        self.data = data

    def travel_to_node(self, node: Node):

        if self.data.player_fuel <= 0:
            print("NO FUEL")
            return False

        self.data.player_fuel -= 1

        self.data.star_map.current_node = node
        node.visited = True

        self.handle_node_event(node)

        return True
    
    def handle_node_event(self, node: Node):

        match node.event_type:

            case "EXIT":
                self.handle_exit_node()

            case "SHOP":
                self.enter_shop()

            case _:
                self.trigger_event(node.event_type)
                
    def handle_exit_node(self):

        if self.data.star_map.sector == 3:

            self.start_boss_fight()

            return

        self.data.star_map.sector += 1

        print(f"Neuer Sektor {self.data.star_map.sector}")

        self.data.star_map.generate_map()

        self.data.player_scrap += 10
        
    def start_boss_fight(self):

        self.data.current_enemy_ship = copy.deepcopy(
            ENEMY_BOSS
        )

        for room in self.data.current_enemy_ship.rooms:
            room.current_power = 1

        self.data.current_state = STATE_COMBAT
        
    def enter_shop(self):

        self.data.current_state = STATE_SHOP
        
    def trigger_event(self, event_type: str):

        scrap, fuel = self.data.event_manager.trigger_event(
            event_type
        )

        self.data.player_scrap += scrap
        self.data.player_fuel += fuel

        self.data.current_state = STATE_EVENT
        
    def continue_event(self):

        if self.data.event_manager.current_event_type == "COMBAT":

            self.start_normal_combat()

        else:

            self.data.current_state = STATE_MAP
            
    def start_normal_combat(self):

        self.data.current_enemy_ship = copy.deepcopy(
            ENEMY_SCOUT
        )

        for room in self.data.current_enemy_ship.rooms:
            room.current_power = 1

        self.data.current_state = STATE_COMBAT
        
    def restart_game(self):
        from classes.Crew import Crew
        from classes.Reactor import Reactor
        from classes.ShieldSystem import ShieldSystem
        from classes.ShipModel import PLAYER_SHIP
        from classes.Weapon import Weapon

        self.data.player_ship = copy.deepcopy(PLAYER_SHIP)
        self.data.player_reactor = Reactor(total_power=PLAYER_START_POWER)
        self.data.player_shield = ShieldSystem()
        self.data.player_crew = [Crew(340, 245), Crew(115, 245)]
        self.data.player_weapons = [
            Weapon("Standard Laser", charge_time=3.0, w_type="LASER"),
            Weapon("Artemis Rakete", charge_time=4.0, w_type="MISSILE", ammo_cost=1),
        ]
        self.data.player_projectiles.clear()
        self.data.player_fuel = PLAYER_START_FUEL
        self.data.player_scrap = PLAYER_START_SCRAP
        self.data.player_missiles = PLAYER_START_MISSILES
        self.data.player_weapon_targets.clear()
        self.data.is_player_targeting = False
        self.data.player_targeting_weapon_idx = None
        self.data.paused = False

        self.data.star_map.sector = 1
        self.data.star_map.generate_map()

        self.data.current_state = STATE_MAP