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
        self.sound = None  # Set by Game after construction

    def travel_to_node(self, node: Node):

        if self.data.player.fuel <= 0:
            self.trigger_event("DISTRESS")
            return False

        self.data.player.fuel -= 1
        self.data.world.star_map.advance_fleet()

        self.data.world.star_map.current_node = node
        node.visited = True

        if self.data.world.star_map.rebel_fleet_x >= node.x:
            if self.sound: self.sound.play("alarm")
            self.start_rebel_pursuit_combat()
        else:
            if self.sound: self.sound.play("jump")
            self.handle_node_event(node)

        return True

    def handle_node_event(self, node: Node):

        match node.event_type:

            case "EXIT":
                self.handle_exit_node()

            case "SHOP":
                self.enter_shop()

            case "TRAINING":
                self.enter_training()

            case _:
                self.trigger_event(node.event_type)

    def handle_exit_node(self):
        sec = self.data.world.star_map.sector
        if sec < 5:
            self.start_mini_boss_fight(sec)
        else:
            self.start_boss_fight()

    def start_rebel_pursuit_combat(self):
        from classes.ShipModel import ENEMY_CRUISER
        self.data.enemy.ship = copy.deepcopy(ENEMY_CRUISER)
        self.data.enemy.ship.name = "Rebellen-Verfolger"
        for room in self.data.enemy.ship.rooms:
            room.current_power = 1
        self.data.enemy.reactor = Reactor(total_power=ENEMY_START_POWER + 2)
        self.data.enemy.shield = ShieldSystem()
        self.data.enemy.weapon = Weapon("Schwerer Abfang-Laser", charge_time=3.2, w_type="HEAVY_LASER", damage=45.0)
        self.data.combat.msg = "ACHTUNG! REBELLENFLOTTE HAT DICH EINGEHOLT!"
        self.data.combat.msg_timer = 3.0
        self.data.current_state = STATE_COMBAT

    def start_mini_boss_fight(self, sector: int):
        from classes.ShipModel import MINI_BOSS_SECTOR_1, MINI_BOSS_SECTOR_2, ENEMY_CRUISER
        template = MINI_BOSS_SECTOR_1 if sector == 1 else (MINI_BOSS_SECTOR_2 if sector == 2 else ENEMY_CRUISER)
        self.data.enemy.ship = copy.deepcopy(template)
        self.data.enemy.ship.name = f"Sektor-{sector} Mini-Boss"

        for room in self.data.enemy.ship.rooms:
            room.current_power = 1

        self.data.enemy.reactor = Reactor(total_power=ENEMY_START_POWER + sector)
        self.data.enemy.shield = ShieldSystem()
        w_type = "FLAK" if sector % 2 == 1 else "HEAVY_LASER"
        self.data.enemy.weapon = Weapon(f"Mini-Boss {w_type.capitalize()}", charge_time=max(2.5, 4.0 - sector * 0.3), w_type=w_type, damage=40.0 + sector * 5)

        self.data.current_state = STATE_COMBAT


        self.data.enemy.reactor = Reactor(total_power=ENEMY_START_POWER + sector)
        self.data.enemy.shield = ShieldSystem()
        w_type = "FLAK" if sector == 1 else "HEAVY_LASER"
        self.data.enemy.weapon = Weapon(f"Mini-Boss {w_type.capitalize()}", charge_time=3.5, w_type=w_type, damage=40.0)

        self.data.current_state = STATE_COMBAT

    def start_boss_fight(self):
        self.data.combat.boss_phase = 1
        self.data.combat.zoltan_shield_hp = 0
        self.data.combat.drone_surge_timer = 18.0
        self.data.combat.boss_teleport_timer = 20.0
        self.data.enemy.ship = copy.deepcopy(ENEMY_BOSS)
        self.data.enemy.ship.hp = 30
        self.data.enemy.ship.max_hp = 30

        for room in self.data.enemy.ship.rooms:
            room.current_power = 1

        self.data.enemy.reactor = Reactor(total_power=ENEMY_START_POWER + 5)
        self.data.enemy.shield = ShieldSystem()
        self.data.enemy.weapon = Weapon("Dreifach-Rakete (Phase 1)", charge_time=4.0, w_type="MISSILE", damage=45.0, ammo_cost=1)
        self.data.combat.msg = "SEKTOR 5 ENDBOSS-KAMPF GESTARTET! FLAGGSCHIFF PHASE 1!"
        self.data.combat.msg_timer = 4.0
        self.data.current_state = STATE_COMBAT

    def enter_shop(self):
        shop_mgr = getattr(self.data, "shop_manager", None)
        if shop_mgr and hasattr(shop_mgr, "refresh_catalog"):
            shop_mgr.refresh_catalog()
        self.data.current_state = STATE_SHOP

    def enter_training(self):
        self.data.current_state = STATE_TRAINING

    def trigger_event(self, event_type: str):

        self.data.world.event_manager.trigger_event(event_type, self.data.player.crew)
        self.data.current_state = STATE_EVENT


    def handle_choice(self, action: str, choice_data: dict):
        has_result = bool(choice_data.get("result_text"))
        if has_result:
            self.data.world.event_manager.result_text = choice_data["result_text"]
            self.data.world.event_manager.pending_action = action

        if action == "BUY_FUEL":
            if self.data.player.scrap >= 10:
                self.data.player.scrap -= 10
                self.data.player.fuel += 2
            if not has_result:
                self.data.current_state = STATE_MAP

        elif action == "SCAVENGE_FUEL":
            self.data.player.fuel += choice_data.get("fuel", 1)
            if not has_result:
                self.data.current_state = STATE_MAP

        elif action in ("CLAIM_RESOURCES", "GIVE_RESOURCES"):
            self.data.player.scrap += choice_data.get("scrap", 0)
            self.data.player.fuel += choice_data.get("fuel", 0)
            self.data.player.missiles += choice_data.get("missiles", 0)
            if not has_result:
                self.data.current_state = STATE_MAP

        elif action == "TAKE_DAMAGE":
            cost_scrap = choice_data.get("cost_scrap", 0)
            self.data.player.scrap = max(0, self.data.player.scrap - cost_scrap)
            dmg = choice_data.get("damage", 0)
            self.data.player.ship.hp = max(0, self.data.player.ship.hp - dmg)
            if not has_result:
                self.data.current_state = STATE_MAP

        elif action == "START_COMBAT":
            if not has_result:
                self.start_normal_combat()

        elif action == "ENTER_SHOP":
            self.enter_shop()

        else:
            if not has_result:
                self.data.current_state = STATE_MAP

    def continue_event(self):
        ev_mgr = self.data.world.event_manager
        pending = getattr(ev_mgr, "pending_action", None)
        ev_type = ev_mgr.current_event_type

        ev_mgr.result_text = ""
        ev_mgr.pending_action = None

        if pending == "START_COMBAT" or (not pending and ev_type == "COMBAT"):
            self.start_normal_combat()
        elif pending == "ENTER_SHOP" or (not pending and ev_type == "SHOP"):
            self.enter_shop()
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
        self.data.player.crew = [Crew(305, 290), Crew(205, 290)]
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
        from managers.save_manager import SaveManager
        self.data.player.unlocked_ships = SaveManager.load_unlocks()
        self.data.player.newly_unlocked_ship = None
        self.data.paused = False

        self.data.world.star_map.sector = 1
        self.data.world.star_map.generate_map()

        self.data.current_state = STATE_MAP