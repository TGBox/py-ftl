import copy

from classes.ShipModel import ENEMY_BOSS, ENEMY_SCOUT
from settings import *


class MapManager:

    def __init__(self, data):
        self.data = data

    def travel_to_node(self, node):

        if self.data.player_fuel <= 0:
            print("NO FUEL")
            return False

        self.data.player_fuel -= 1

        self.data.star_map.current_node = node
        node.visited = True

        self.handle_node_event(node)

        return True
    
    def handle_node_event(self, node):

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
        
    def trigger_event(self, event_type):

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

        from classes.ShipModel import PLAYER_SHIP

        self.data.player_ship = copy.deepcopy(
            PLAYER_SHIP
        )

        self.data.star_map.sector = 1
        self.data.star_map.generate_map()

        self.data.player_fuel = 5
        self.data.player_scrap = 20
        self.data.player_missiles = 6

        self.data.player_weapon_targets.clear()

        self.data.current_state = STATE_MAP