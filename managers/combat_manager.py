from classes.GameData import GameData
from classes.Projectile import Projectile

from managers.state_manager import StateManager
from settings import *


#if not paused and current_state == STATE_COMBAT:
#    combat_msg_timer = max(0.0, combat_msg_timer - dt)
#
#    for c in crew_members:
#      c.update(dt, player_ship.rooms)  #[cite: 4]
#
#    player_shield.update(dt, player_ship.rooms[0].current_power)  #[cite: 10]
#    enemy_shield.update(dt, current_enemy.rooms[0].current_power)  #[cite: 10]
#
#    weapon_powered = player_ship.rooms[1].current_power > 0
#    for w in player_weapons:
#      w.update(dt, weapon_powered)  #[cite: 13]
#
#    # NEU: Autofire feuert nur Waffen ab, für die exakt eine Schusslinie definiert wurde
#    if autofire_enabled:
#      weapon_room = player_ship.rooms[1]
#      for idx, w in enumerate(player_weapons):
#        if w.is_ready() and idx in weapon_targets:  #[cite: 13]
#          target_room, start_p, end_p = weapon_targets[idx]
#          # Prüfen ob Zielraum noch existiert/lebt
#          if target_room in current_enemy.rooms:
#            if w.ammo_cost > 0 and missiles < w.ammo_cost:
#              combat_msg = "KEINE RAKETEN MEHR!"
#              combat_msg_timer = 1.5
#            else:
#              if w.ammo_cost > 0:
#                missiles -= w.ammo_cost
#              projectiles.append(
#                  Projectile(
#                      weapon_room.rect.center,
#                      end_p,
#                      target_room,
#                      is_player_shot=True,
#                      w_type=w.w_type,
#                      shield_pierce=w.shield_pierce,
#                      damage=w.damage,
#                  )
#              )  #[cite: 1, 7]
#              w.reset()  #[cite: 13]
#
#    enemy_weapon.update(
#        dt,
#        current_enemy.rooms[1].current_power > 0
#        and current_enemy.rooms[1].health > 20.0,
#    )  #[cite: 13]
#
#    if enemy_weapon.is_ready():  #[cite: 13]
#      target_room = random.choice(player_ship.rooms)
#      projectiles.append(
#          Projectile(
#              current_enemy.rooms[1].rect.center,
#              target_room.rect.center,
#              target_room=target_room,
#              is_player_shot=False,
#              w_type=enemy_weapon.w_type,
#              shield_pierce=enemy_weapon.shield_pierce,
#              damage=enemy_weapon.damage,
#          )
#      )  #[cite: 1, 7]
#      enemy_weapon.reset()  #[cite: 13]
#
#    for p in projectiles[:]:
#      p.update(dt)  #[cite: 7]
#      if not p.alive:
#        if p.is_player_shot:
#          enemy_evade = current_enemy.rooms[2].current_power * 0.15
#          if random.random() < enemy_evade:
#            combat_msg = "FEIND IST AUSGEWICHEN!"
#            combat_msg_timer = 1.5
#          else:
#            hit_successful = False
#            if p.w_type == "MISSILE":
#              hit_successful = True
#            elif p.w_type == "BEAM":
#              if enemy_shield.current_layers <= p.shield_pierce:  #[cite: 10]
#                hit_successful = True
#              else:
#                enemy_shield.attempt_block()  #[cite: 10]
#            else:
#              if not enemy_shield.attempt_block():  #[cite: 10]
#                hit_successful = True
#
#            if hit_successful:
#              current_enemy.hp = max(0, current_enemy.hp - 1)
#              p.target_room.apply_damage(p.damage, enemy_reactor)  #[cite: 8, 9]
#        else:
#          player_evade = player_ship.rooms[2].current_power * 0.20
#          if random.random() < player_evade:
#            combat_msg = "AUSGEWICHEN!"
#            combat_msg_timer = 1.5
#          else:
#            hit_successful = False
#            if p.w_type == "MISSILE":
#              hit_successful = True
#            elif p.w_type == "BEAM":
#              if player_shield.current_layers <= p.shield_pierce:  #[cite: 10]
#                hit_successful = True
#              else:
#                player_shield.attempt_block()  #[cite: 10]
#            else:
#              if not player_shield.attempt_block():  #[cite: 10]
#                hit_successful = True
#
#            if hit_successful:
#              player_ship.hp = max(0, player_ship.hp - 1)
#              p.target_room.apply_damage(p.damage, reactor)  #[cite: 8, 9]
#
#        projectiles.remove(p)
#
#    if current_enemy.hp <= 0:
#      scrap += 20
#      missiles += 2
#      projectiles.clear()
#      weapon_targets.clear()
#      if star_map.sector == 3 and current_enemy.name == "Flaggschiff":  #[cite: 12]
#        current_state = STATE_VICTORY  #[cite: 1]
#      else:
#        print(f"{current_state} -> {STATE_MAP}")
#        current_state = STATE_MAP  #[cite: 1]
#
#    if player_ship.hp <= 0:
#      projectiles.clear()
#      weapon_targets.clear()
#      current_state = STATE_GAME_OVER  #[cite: 1]

import random

from classes.Projectile import Projectile
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

        ...

    def handle_enemy_hit(self, projectile: Projectile):

        ...

    def calculate_player_hit(self, projectile: Projectile):

        ...

    def calculate_enemy_hit(self, projectile: Projectile):

        ...
        
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