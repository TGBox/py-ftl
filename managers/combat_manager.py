import random

from classes.Crew import Crew
from classes.GameData import GameData
from classes.Projectile import Projectile
from managers.state_manager import StateManager
from settings import *


class CombatManager:

    def __init__(self, data: GameData, state_manager: StateManager):
        self.data = data
        self.state_manager = state_manager
        self.enemy_crew: list[Crew] = []

    def update(self, dt: float):
        """Wird einmal pro Frame aufgerufen."""

        if self.data.paused:
            return

        if self.data.current_state != STATE_COMBAT:
            return

        self.data.combat.msg_timer = max(
            0.0,
            self.data.combat.msg_timer - dt
        )

        self.update_crew(dt)
        self.update_shields(dt)
        self.update_weapons(dt)
        self.update_enemy_weapon(dt)
        self.update_projectiles(dt)
        self.check_end_of_battle()

    def update_crew(self, dt: float):
        # Sauerstoff & Erstickungs-Schaden (SRS Kap. 5.1)
        for room in self.data.player.ship.rooms:
            room.update_oxygen(dt)

        for crew in self.data.player.crew:
            crew.update(dt, self.data.player.ship.rooms)
            if crew.current_room and crew.current_room.oxygen < 20.0:
                crew.hp = max(0.0, crew.hp - 8.0 * dt)

        # Gegnerische Crew initialisieren & updaten
        if not self.enemy_crew and len(self.data.enemy.ship.rooms) > 0:
            for r in self.data.enemy.ship.rooms:
                self.enemy_crew.append(Crew(r.rect.centerx, r.rect.centery, name="Pirate", is_enemy=True))

        for e_crew in self.enemy_crew:
            e_crew.update(dt, self.data.enemy.ship.rooms)


    def update_shields(self, dt: float):

        self.data.player.shield.update(
            dt,
            self.data.player.ship.rooms[0].current_power
        )

        self.data.enemy.shield.update(
            dt,
            self.data.enemy.ship.rooms[0].current_power
        )

    def update_weapons(self, dt: float):

        weapon_powered = (
            self.data.player.ship.rooms[1].current_power > 0
        )

        # Waffen-Bemannungsbonus (falls Crew in Waffenraum steht)
        weapon_manned = any(
            c.current_room == self.data.player.ship.rooms[1] for c in self.data.player.crew
        )
        charge_mult = 1.25 if weapon_manned else 1.0

        for weapon in self.data.player.weapons:
            weapon.update(dt * charge_mult, weapon_powered)

        if self.data.combat.autofire_enabled:
            self.fire_autofire_weapons()

    def fire_autofire_weapons(self):

        weapon_room = self.data.player.ship.rooms[1]

        for idx, weapon in enumerate(self.data.player.weapons):

            if not weapon.is_ready():
                continue

            if idx not in self.data.combat.weapon_targets:
                continue

            target_room, _, end_pos = \
                self.data.combat.weapon_targets[idx]

            if target_room not in self.data.enemy.ship.rooms:
                continue

            if (
                weapon.ammo_cost > 0
                and self.data.player.missiles < weapon.ammo_cost
            ):
                self.state_manager.show_message("KEINE RAKETEN MEHR!")
                continue

            if weapon.ammo_cost > 0:
                self.data.player.missiles -= weapon.ammo_cost

            self.data.player.projectiles.append(
                Projectile(
                    weapon_room.rect.center,
                    end_pos,
                    target_room,
                    is_player_shot=True,
                    w_type=weapon.w_type,
                    shield_pierce=weapon.shield_pierce,
                    damage=weapon.damage,
                )
            )

            weapon.reset()

    def update_enemy_weapon(self, dt: float):

        weapon = self.data.enemy.weapon

        weapon.update(
            dt,
            self.data.enemy.ship.rooms[1].current_power > 0
            and self.data.enemy.ship.rooms[1].health > 20
        )

        if not weapon.is_ready():
            return

        target_room = random.choice(self.data.player.ship.rooms)

        self.data.player.projectiles.append(
            Projectile(
                self.data.enemy.ship.rooms[1].rect.center,
                target_room.rect.center,
                target_room=target_room,
                is_player_shot=False,
                w_type=weapon.w_type,
                shield_pierce=weapon.shield_pierce,
                damage=weapon.damage,
            )
        )

        weapon.reset()

    def update_projectiles(self, dt: float):

        for projectile in self.data.player.projectiles[:]:

            projectile.update(dt)

            if projectile.alive:
                continue

            if projectile.is_player_shot:
                self.handle_player_hit(projectile)
            else:
                self.handle_enemy_hit(projectile)

            self.data.player.projectiles.remove(projectile)

    def handle_player_hit(self, projectile: Projectile):
        # SRS 6.2 Evasion Berechnung
        base_engine = self.data.enemy.ship.rooms[2].current_power * 0.10 if len(self.data.enemy.ship.rooms) > 2 else 0.10
        enemy_evade = base_engine

        if random.random() < enemy_evade:
            self.show_message("FEIND IST AUSGEWICHEN!")
        else:
            hit_successful = False
            if projectile.w_type == "MISSILE":
                hit_successful = True
            elif projectile.w_type == "BEAM":
                if self.data.enemy.shield.current_layers <= projectile.shield_pierce:
                    hit_successful = True
                else:
                    self.data.enemy.shield.attempt_block()
            else:
                if not self.data.enemy.shield.attempt_block():
                    hit_successful = True

            if hit_successful:
                if projectile.w_type == "BEAM":
                    # Beam schneidet mehrere Räume per Liniensegment-Schnittpunkt (SRS 6.2)
                    intersected_rooms = projectile.get_intersected_rooms(self.data.enemy.ship.rooms)
                    for room in intersected_rooms:
                        self.data.enemy.ship.hp = max(0, self.data.enemy.ship.hp - 1)
                        room.apply_damage(projectile.damage, self.data.enemy.reactor)
                else:
                    self.data.enemy.ship.hp = max(0, self.data.enemy.ship.hp - 1)
                    projectile.target_room.apply_damage(projectile.damage, self.data.enemy.reactor)

    def handle_enemy_hit(self, projectile: Projectile):
        # SRS 6.2 Evasion Formel: E = (E_Base_Engine + C_Engine_Bonus + C_Pilot_Bonus) * A_Multiplier + S_Cloak
        e_base_engine = self.data.player.ship.rooms[2].current_power * 0.10 if len(self.data.player.ship.rooms) > 2 else 0.10
        c_pilot_bonus = 0.10 if any(c.current_room == self.data.player.ship.rooms[2] for c in self.data.player.crew) else 0.0
        c_engine_bonus = 0.05 if any(c.current_room == self.data.player.ship.rooms[0] for c in self.data.player.crew) else 0.0
        a_multiplier = 1.0 if c_pilot_bonus > 0 else 0.0
        s_cloak = 0.0

        player_evade = (e_base_engine + c_engine_bonus + c_pilot_bonus) * (a_multiplier if c_pilot_bonus > 0 else 1.0) + s_cloak

        if random.random() < player_evade:
            self.show_message("AUSGEWICHEN!")
        else:
            hit_successful = False
            if projectile.w_type == "MISSILE":
                hit_successful = True
            elif projectile.w_type == "BEAM":
                if self.data.player.shield.current_layers <= projectile.shield_pierce:
                    hit_successful = True
                else:
                    self.data.player.shield.attempt_block()
            else:
                if not self.data.player.shield.attempt_block():
                    hit_successful = True

            if hit_successful:
                if projectile.w_type == "BEAM":
                    intersected_rooms = projectile.get_intersected_rooms(self.data.player.ship.rooms)
                    for room in intersected_rooms:
                        self.data.player.ship.hp = max(0, self.data.player.ship.hp - 1)
                        room.apply_damage(projectile.damage, self.data.player.reactor)
                else:
                    self.data.player.ship.hp = max(0, self.data.player.ship.hp - 1)
                    projectile.target_room.apply_damage(projectile.damage, self.data.player.reactor)

    def check_end_of_battle(self):

        if self.data.enemy.ship.hp <= 0:

            self.player_won()

            return

        if self.data.player.ship.hp <= 0:

            self.player_lost()

    def calculate_stochastic_rewards(self, reward_tier: str = "Medium") -> tuple[int, int]:
        """SRS 6.3 Stochastische Belohnungsberechnung: Scrap = floor(B_Sector * V_Tier)."""
        sector = self.data.world.star_map.sector
        b_sector = 15 + sector * 10
        if reward_tier == "Low":
            v_tier = random.uniform(0.5, 0.7)
        elif reward_tier == "High":
            v_tier = random.uniform(1.3, 1.55)
        else:  # Medium
            v_tier = random.uniform(0.8, 1.3)

        scrap = int(b_sector * v_tier)
        missiles = random.randint(1, 3)

        # 3% bis 6% Chance auf Bonus-Drop (SRS Kap. 6.3)
        drop_chance = 0.06 if reward_tier == "High" else 0.03
        if random.random() < drop_chance:
            self.data.player.missiles += 2
            self.show_message("BONUS-BEUTE GEFUNDEN! (+2 Raketen)")

        return scrap, missiles

    def player_won(self):

        is_mini_boss = "Mini-Boss" in self.data.enemy.ship.name
        tier = "High" if (self.data.enemy.ship.name == "Flaggschiff" or is_mini_boss) else "Medium"
        scrap_reward, missile_reward = self.calculate_stochastic_rewards(tier)

        self.data.player.scrap += scrap_reward
        self.data.player.missiles += missile_reward
        self.enemy_crew.clear()

        self.data.player.projectiles.clear()
        self.data.combat.weapon_targets.clear()

        if (
            self.data.world.star_map.sector == 3
            and self.data.enemy.ship.name == "Flaggschiff"
        ):
            self.data.current_state = STATE_VICTORY
        elif is_mini_boss:
            self.data.world.star_map.sector += 1
            self.data.world.star_map.generate_map()
            self.data.player.scrap += 25
            self.show_message(f"MINI-BOSS BESIEGT! WEITER ZU SEKTOR {self.data.world.star_map.sector}")
            self.data.current_state = STATE_MAP
        else:
            self.data.current_state = STATE_MAP



    def player_lost(self):

        self.data.player.projectiles.clear()
        self.data.combat.weapon_targets.clear()
        self.enemy_crew.clear()

        self.data.current_state = STATE_GAME_OVER

    def show_message(self, text: str):

        self.data.combat.msg = text
        self.data.combat.msg_timer = 1.5

