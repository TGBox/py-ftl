import copy

from classes.GameData import GameData
from classes.Node import Node
from classes.Reactor import Reactor
from classes.ShieldSystem import ShieldSystem
from classes.ShipModel import ENEMY_BOSS, ENEMY_SCOUT
from classes.Weapon import Weapon
from settings import *


class MapManager:

    def __init__(self, data: GameData):
        self.data = data

    def travel_to_node(self, node: Node):

        if self.data.player.fuel <= 0:
            self.trigger_event("DISTRESS")
            return False

        self.data.player.fuel -= 1
        self.data.world.star_map.advance_fleet()

        self.data.world.star_map.current_node = node
        node.visited = True

        if self.data.world.star_map.rebel_fleet_x >= node.x:
            self.start_normal_combat()
        else:
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
        sec = self.data.world.star_map.sector
        if sec == 1:
            self.start_mini_boss_fight(1)
        elif sec == 2:
            self.start_mini_boss_fight(2)
        elif sec == 3:
            self.start_boss_fight()

    def start_mini_boss_fight(self, sector: int):
        from classes.ShipModel import MINI_BOSS_SECTOR_1, MINI_BOSS_SECTOR_2
        template = MINI_BOSS_SECTOR_1 if sector == 1 else MINI_BOSS_SECTOR_2
        self.data.enemy.ship = copy.deepcopy(template)

        for room in self.data.enemy.ship.rooms:
            room.current_power = 1

        self.data.enemy.reactor = Reactor(total_power=ENEMY_START_POWER + sector)
        self.data.enemy.shield = ShieldSystem()
        w_type = "FLAK" if sector == 1 else "HEAVY_LASER"
        self.data.enemy.weapon = Weapon(f"Mini-Boss {w_type.capitalize()}", charge_time=3.5, w_type=w_type, damage=40.0)

        self.data.current_state = STATE_COMBAT

    def start_boss_fight(self):

        self.data.enemy.ship = copy.deepcopy(
            ENEMY_BOSS
        )


        for room in self.data.enemy.ship.rooms:
            room.current_power = 1

        self.data.enemy.reactor = Reactor(total_power=ENEMY_START_POWER)
        self.data.enemy.shield = ShieldSystem()
        self.data.enemy.weapon = Weapon("Laser", charge_time=4.5, w_type="LASER")

        self.data.current_state = STATE_COMBAT

    def enter_shop(self):

        self.data.current_state = STATE_SHOP

    def trigger_event(self, event_type: str):

        self.data.world.event_manager.trigger_event(event_type, self.data.player.crew)
        self.data.current_state = STATE_EVENT


    def handle_choice(self, action: str, choice_data: dict):
        if action == "BUY_FUEL":
            if self.data.player.scrap >= 10:
                self.data.player.scrap -= 10
                self.data.player.fuel += 2
            self.data.current_state = STATE_MAP

        elif action == "SCAVENGE_FUEL":
            self.data.player.fuel += 1
            self.data.current_state = STATE_MAP

        elif action == "CLAIM_RESOURCES":
            self.data.player.scrap += choice_data.get("scrap", 0)
            self.data.player.fuel += choice_data.get("fuel", 0)
            self.data.current_state = STATE_MAP

        elif action == "START_COMBAT":
            self.start_normal_combat()

        elif action == "ENTER_SHOP":
            self.enter_shop()

        else:
            self.data.current_state = STATE_MAP

    def continue_event(self):

        if self.data.world.event_manager.current_event_type == "COMBAT":

            self.start_normal_combat()

        else:

            self.data.current_state = STATE_MAP

    def start_normal_combat(self):
        import random
        from classes.ShipModel import ENEMY_SCOUT, ENEMY_FIGHTER, ENEMY_BOMBER, ENEMY_CRUISER

        sector = self.data.world.star_map.sector
        if sector == 1:
            template = random.choice([ENEMY_SCOUT, ENEMY_FIGHTER])
        elif sector == 2:
            template = random.choice([ENEMY_FIGHTER, ENEMY_BOMBER])
        else:
            template = random.choice([ENEMY_BOMBER, ENEMY_CRUISER])

        self.data.enemy.ship = copy.deepcopy(template)

        for room in self.data.enemy.ship.rooms:
            room.current_power = 1

        self.data.enemy.reactor = Reactor(total_power=ENEMY_START_POWER + sector - 1)
        self.data.enemy.shield = ShieldSystem()

        w_type = random.choice(["LASER", "MISSILE", "BEAM"])
        w_name = "Feind " + w_type.capitalize()
        self.data.enemy.weapon = Weapon(w_name, charge_time=max(2.5, 4.5 - sector * 0.4), w_type=w_type)

        self.data.current_state = STATE_COMBAT


    def restart_game(self):
        from classes.Crew import Crew
        from classes.Reactor import Reactor
        from classes.ShieldSystem import ShieldSystem
        from classes.ShipModel import PLAYER_SHIP
        from classes.Weapon import Weapon

        self.data.player.ship = copy.deepcopy(PLAYER_SHIP)
        self.data.player.reactor = Reactor(total_power=PLAYER_START_POWER)
        self.data.player.shield = ShieldSystem()
        self.data.player.crew = [Crew(340, 245), Crew(115, 245)]
        self.data.player.weapons = [
            Weapon("Standard Laser", charge_time=3.0, w_type="LASER"),
            Weapon("Artemis Rakete", charge_time=4.0, w_type="MISSILE", ammo_cost=1),
        ]
        self.data.player.projectiles.clear()
        self.data.player.fuel = PLAYER_START_FUEL
        self.data.player.scrap = PLAYER_START_SCRAP
        self.data.player.missiles = PLAYER_START_MISSILES
        self.data.combat.weapon_targets.clear()
        self.data.combat.is_targeting = False
        self.data.combat.target_weapon_idx = None
        self.data.paused = False

        self.data.world.star_map.sector = 1
        self.data.world.star_map.generate_map()

        self.data.current_state = STATE_MAP