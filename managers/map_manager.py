from typing import TYPE_CHECKING


import copy
import random
from typing import Any

from classes.GameData import GameData
from classes.Node import Node
from classes.Reactor import Reactor
from classes.ShieldSystem import ShieldSystem
from classes.ShipModel import ENEMY_BOSS
from classes.Weapon import Weapon
from managers.sound_manager import SoundManager
from settings import *

if TYPE_CHECKING:
    from game import Game

class MapManager:

    def __init__(self, data: GameData) -> None:
        self.data: GameData = data
        self.game: "Game | None" = None   # Set by Game after construction
        self.sound: SoundManager | None = None  # Set by Game after construction

    def travel_to_node(self, node: Node) -> bool:

        if self.data.player.fuel <= 0:
            self.trigger_event("DISTRESS")
            return False

        self.data.player.fuel -= 1
        self.data.world.star_map.advance_fleet()

        self.data.world.star_map.current_node = node
        node.visited = True

        # Auto-Save progress on node jump (if enabled in settings)
        if getattr(self.data, "auto_save_enabled", False):
            from managers.save_manager import SaveManager
            try:
                assert self.game is not None
                SaveManager.save_game(self.data, self.game)
            except Exception as e:
                print(f"Auto-Save Fehler: {e}")

        if self.data.world.star_map.rebel_fleet_x >= node.x:
            if self.sound: self.sound.play("alarm")
            self.start_rebel_pursuit_combat()
        else:
            if self.sound: self.sound.play("jump")
            self.handle_node_event(node)

        return True

    def handle_node_event(self, node: Node) -> None:

        match node.event_type:

            case "EXIT":
                self.handle_exit_node()

            case "SHOP":
                self.enter_shop()

            case "TRAINING":
                self.enter_training()

            case _:
                self.trigger_event(node.event_type)

    def handle_exit_node(self) -> None:
        sec = self.data.world.star_map.sector
        if sec < 5:
            self.start_mini_boss_fight(sec)
        else:
            self.start_boss_fight()

    def start_rebel_pursuit_combat(self) -> None:
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

    def start_mini_boss_fight(self, sector: int) -> None:
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

    def start_boss_fight(self) -> None:
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

    def enter_shop(self) -> None:
        shop_mgr = getattr(self.data, "shop_manager", None)
        if shop_mgr and hasattr(shop_mgr, "refresh_catalog"):
            shop_mgr.refresh_catalog()
        self.data.current_state = STATE_SHOP

    def enter_training(self) -> None:
        self.data.current_state = STATE_TRAINING

    def trigger_event(self, event_type: str) -> None:
        if self.data.player.fuel <= 0 and event_type == "DISTRESS" and hasattr(self.data, "achievements"):
            assert self.game is not None
            self.game.achievement_manager.unlock("survivor")

        assert self.game is not None
        self.game.event_manager.trigger_event(
            event_type, self.data.player.crew, self.data.player.fuel
        )
        self.data.current_state = STATE_EVENT

    def handle_choice(self, action: str, choice_data: dict[str, Any]) -> None:
        if hasattr(self.game, "achievements"):
            evt_count = getattr(self.data, "events_completed_count", 0) + 1
            self.events_completed_count = evt_count
            if evt_count >= 10:
                assert self.game is not None
                self.game.achievement_manager.unlock("event_explorer")

        has_result = bool(choice_data.get("result_text")) or "outcomes" in choice_data

        # 1. Stochastische Risiko-Auswertung (Erfolg vs. Fehlschlag)
        if "outcomes" in choice_data and isinstance(choice_data["outcomes"], list):
            outcomes: list[dict[str, Any]] = choice_data.get("outcomes", [])
            assert isinstance(outcomes, list)
            r = random.random()
            cum_prob = 0.0
            chosen = outcomes[-1]
            for o in outcomes:
                cum_prob += o.get("chance", 0.5)
                if r <= cum_prob:
                    chosen = o
                    break
            choice_data = chosen
            action = choice_data.get("action", action)
            has_result = bool(choice_data.get("result_text"))

        if has_result:
            self.data.world.event_manager.result_text = choice_data.get("result_text", "")
            self.data.world.event_manager.pending_action = action

        # 2. Ressourcen-Änderungen (Positiv & Negativ)
        if choice_data.get("cost_scrap", 0) > 0:
            self.data.player.scrap = max(0, self.data.player.scrap - choice_data["cost_scrap"])
        if choice_data.get("cost_fuel", 0) > 0:
            self.data.player.fuel = max(0, self.data.player.fuel - choice_data["cost_fuel"])
        if choice_data.get("cost_missiles", 0) > 0:
            self.data.player.missiles = max(0, self.data.player.missiles - choice_data["cost_missiles"])

        # 3. Negative Gefahren & Schaden anwenden
        c_dmg = choice_data.get("crew_damage", 0)
        if c_dmg > 0 and self.data.player.crew:
            affected = random.choice(self.data.player.crew)
            affected.hp = max(0.0, affected.hp - c_dmg)
            if affected.hp <= 0:
                self.data.player.crew.remove(affected)

        if choice_data.get("fire_room", False) and self.data.player.ship.rooms:
            r_fire = random.choice(self.data.player.ship.rooms)
            r_fire.fire_level = min(100.0, r_fire.fire_level + 60.0)

        if choice_data.get("breach_room", False) and self.data.player.ship.rooms:
            r_breach = random.choice(self.data.player.ship.rooms)
            r_breach.has_breach = True

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
            self.data.player.scrap = max(0, self.data.player.scrap + choice_data.get("scrap", 0))
            self.data.player.fuel = max(0, self.data.player.fuel + choice_data.get("fuel", 0))
            self.data.player.missiles = max(0, self.data.player.missiles + choice_data.get("missiles", 0))
            self.data.player.drone_parts = max(0, self.data.player.drone_parts + choice_data.get("drones", choice_data.get("drone_parts", 0)))
            if not has_result:
                self.data.current_state = STATE_MAP

        elif action in ("FLEE", "TRY_ESCAPE", "ESCAPE") or choice_data.get("is_escape", False):
            if random.random() < 0.30:
                if random.random() < 0.50:
                    dmg = random.randint(2, 5)
                    self.data.player.ship.hp = max(0, self.data.player.ship.hp - dmg)
                    self.data.world.event_manager.result_text = (
                        f"FLUCHTVERSUCH MISSLUNGEN! Dein Schiff wird beim Abbiegen unter Beschuss genommen (-{dmg} Hüllenschaden)!"
                    )
                    self.data.world.event_manager.pending_action = None
                else:
                    self.data.world.event_manager.result_text = (
                        "FLUCHTVERSUCH MISSLUNGEN! Das gegnerische Schiff blockiert den Sprungpfad und erzwingt das Gefecht!"
                    )
                    self.data.world.event_manager.pending_action = "START_COMBAT"
            else:
                if not has_result:
                    self.data.world.event_manager.result_text = "FLUCHT ERFOLGREICH! Du entkommst der Gefahr ohne weiteren Schaden."
                    self.data.world.event_manager.pending_action = None
                elif not getattr(self.data.world.event_manager, "result_text", ""):
                    self.data.world.event_manager.result_text = choice_data.get("result_text", "Flucht erfolgreich.")

        elif action == "TAKE_DAMAGE":
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

    def continue_event(self) -> None:
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

    def start_normal_combat(self) -> None:
        import random
        from classes.ShipModel import (
            ENEMY_SCOUT, ENEMY_FIGHTER, ENEMY_BOMBER, ENEMY_CRUISER,
            ENEMY_MANTIS_BOARDER, ENEMY_ZOLTAN_FRIGATE, ENEMY_ROCK_WARSHIP, ENEMY_DRONE_CARRIER
        )

        sector = self.data.world.star_map.sector
        sector_type = getattr(self.data.world.star_map, "sector_type", "Zivil")

        if "Nebel" in sector_type:
            pool = [ENEMY_SCOUT, ENEMY_ZOLTAN_FRIGATE, ENEMY_DRONE_CARRIER]
        elif "Piraten" in sector_type:
            pool = [ENEMY_MANTIS_BOARDER, ENEMY_ROCK_WARSHIP, ENEMY_BOMBER]
        elif "Rebellen" in sector_type:
            pool = [ENEMY_FIGHTER, ENEMY_CRUISER, ENEMY_DRONE_CARRIER]
        else:
            if sector == 1:
                pool = [ENEMY_SCOUT, ENEMY_FIGHTER]
            elif sector == 2:
                pool = [ENEMY_FIGHTER, ENEMY_BOMBER, ENEMY_ZOLTAN_FRIGATE]
            else:
                pool = [ENEMY_BOMBER, ENEMY_CRUISER, ENEMY_ROCK_WARSHIP, ENEMY_MANTIS_BOARDER]

        template = random.choice(pool)
        self.data.enemy.ship = copy.deepcopy(template)

        for room in self.data.enemy.ship.rooms:
            room.current_power = 1

        self.data.enemy.reactor = Reactor(total_power=ENEMY_START_POWER + sector - 1)
        self.data.enemy.shield = ShieldSystem()

        w_type = random.choice(["LASER", "MISSILE", "BEAM"])
        w_name = "Feind " + w_type.capitalize()
        self.data.enemy.weapon = Weapon(w_name, charge_time=max(2.5, 4.5 - sector * 0.4), w_type=w_type)

        self.data.current_state = STATE_COMBAT

    def restart_game(self) -> None:
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