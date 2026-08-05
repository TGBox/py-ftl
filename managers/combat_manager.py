import random

from classes.GameData import GameData
from classes.Projectile import Projectile
from managers.state_manager import StateManager
from settings import *


class CombatManager:

    def __init__(self, data: GameData, state_manager: StateManager):
        self.data = data
        self.state_manager = state_manager

    def update(self, dt: float):
        """Wird einmal pro Frame aufgerufen."""

        if self.data.paused:
            return

        if self.data.current_state != STATE_COMBAT:
            return

        self.data.combat_msg_timer = max(
            0.0,
            self.data.combat_msg_timer - dt
        )

        self.update_crew(dt)
        self.update_shields(dt)
        self.update_weapons(dt)
        self.update_enemy_weapon(dt)
        self.update_projectiles(dt)
        self.check_end_of_battle()

    def update_crew(self, dt: float):
        for crew in self.data.player_crew:
            crew.update(dt, self.data.player_ship.rooms)

    def update_shields(self, dt: float):

        self.data.player_shield.update(
            dt,
            self.data.player_ship.rooms[0].current_power
        )

        self.data.enemy_shield.update(
            dt,
            self.data.current_enemy_ship.rooms[0].current_power
        )

    def update_weapons(self, dt: float):

        weapon_powered = (
            self.data.player_ship.rooms[1].current_power > 0
        )

        for weapon in self.data.player_weapons:
            weapon.update(dt, weapon_powered)

        if self.data.player_autofire_enabled:
            self.fire_autofire_weapons()

    def fire_autofire_weapons(self):

        weapon_room = self.data.player_ship.rooms[1]

        for idx, weapon in enumerate(self.data.player_weapons):

            if not weapon.is_ready():
                continue

            if idx not in self.data.player_weapon_targets:
                continue

            target_room, _, end_pos = \
                self.data.player_weapon_targets[idx]

            if target_room not in self.data.current_enemy_ship.rooms:
                continue

            if (
                weapon.ammo_cost > 0
                and self.data.player_missiles < weapon.ammo_cost
            ):
                self.state_manager.show_message("KEINE RAKETEN MEHR!")
                continue

            if weapon.ammo_cost > 0:
                self.data.player_missiles -= weapon.ammo_cost

            self.data.player_projectiles.append(
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

        weapon = self.data.enemy_weapon

        weapon.update(
            dt,
            self.data.current_enemy_ship.rooms[1].current_power > 0
            and self.data.current_enemy_ship.rooms[1].health > 20
        )

        if not weapon.is_ready():
            return

        target_room = random.choice(self.data.player_ship.rooms)

        self.data.player_projectiles.append(
            Projectile(
                self.data.current_enemy_ship.rooms[1].rect.center,
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

        for projectile in self.data.player_projectiles[:]:

            projectile.update(dt)

            if projectile.alive:
                continue

            if projectile.is_player_shot:
                self.handle_player_hit(projectile)
            else:
                self.handle_enemy_hit(projectile)

            self.data.player_projectiles.remove(projectile)

    def handle_player_hit(self, projectile: Projectile):
        enemy_evade = self.data.current_enemy_ship.rooms[2].current_power * 0.15
        if random.random() < enemy_evade:
            self.show_message("FEIND IST AUSGEWICHEN!")
        else:
            hit_successful = False
            if projectile.w_type == "MISSILE":
                hit_successful = True
            elif projectile.w_type == "BEAM":
                if self.data.enemy_shield.current_layers <= projectile.shield_pierce:
                    hit_successful = True
                else:
                    self.data.enemy_shield.attempt_block()
            else:
                if not self.data.enemy_shield.attempt_block():
                    hit_successful = True

            if hit_successful:
                self.data.current_enemy_ship.hp = max(0, self.data.current_enemy_ship.hp - 1)
                projectile.target_room.apply_damage(projectile.damage, self.data.enemy_reactor)

    def handle_enemy_hit(self, projectile: Projectile):
        player_evade = self.data.player_ship.rooms[2].current_power * 0.20
        if random.random() < player_evade:
            self.show_message("AUSGEWICHEN!")
        else:
            hit_successful = False
            if projectile.w_type == "MISSILE":
                hit_successful = True
            elif projectile.w_type == "BEAM":
                if self.data.player_shield.current_layers <= projectile.shield_pierce:
                    hit_successful = True
                else:
                    self.data.player_shield.attempt_block()
            else:
                if not self.data.player_shield.attempt_block():
                    hit_successful = True

            if hit_successful:
                self.data.player_ship.hp = max(0, self.data.player_ship.hp - 1)
                projectile.target_room.apply_damage(projectile.damage, self.data.player_reactor)

    def check_end_of_battle(self):

        if self.data.current_enemy_ship.hp <= 0:

            self.player_won()

            return

        if self.data.player_ship.hp <= 0:

            self.player_lost()

    def player_won(self):

        self.data.player_scrap += 20
        self.data.player_missiles += 2

        self.data.player_projectiles.clear()
        self.data.player_weapon_targets.clear()

        if (
            self.data.star_map.sector == 3
            and self.data.current_enemy_ship.name == "Flaggschiff"
        ):
            self.data.current_state = STATE_VICTORY
        else:
            self.data.current_state = STATE_MAP

    def player_lost(self):

        self.data.player_projectiles.clear()
        self.data.player_weapon_targets.clear()

        self.data.current_state = STATE_GAME_OVER

    def show_message(self, text: str):

        self.data.combat_msg = text
        self.data.combat_msg_timer = 1.5