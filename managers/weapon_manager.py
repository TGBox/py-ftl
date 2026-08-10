from typing import TYPE_CHECKING

import pygame

from classes.GameData import GameData
from classes.Projectile import Projectile
from classes.Room import Room
if TYPE_CHECKING:
    from game import Game



class WeaponManager:

    def __init__(self, data: GameData):
        self.data = data
        self.game: "Game | None" = None   # Set by Game after construction

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    def update(self, dt: float):

        weapon_powered = (
            self.data.player.ship.rooms[1].current_power > 0
        )
        assert self.data.player.weapons is not None
        for weapon in self.data.player.weapons:
                weapon.update(dt, weapon_powered)

        if self.data.combat.autofire_enabled:
            self.handle_autofire()

    # --------------------------------------------------
    # WAFFEN AUSWÄHLEN
    # --------------------------------------------------

    def select_weapon(self, mx: float, my: float):

        weapon_room = self.data.player.ship.rooms[1]

        assert self.data.player.weapons is not None
        for idx, weapon in enumerate(self.data.player.weapons):

            bar_x = 30 + idx * 115

            bar_rect = pygame.Rect(
                bar_x,
                335,
                105,
                15,
            )

            if (
                bar_rect.collidepoint(mx, my)
                or weapon_room.rect.collidepoint(mx, my)
            ):

                if not weapon.is_ready():
                    return False

                self.data.combat.is_targeting = True
                self.data.combat.target_weapon_idx = idx
                self.data.combat.start_pos = (
                    weapon_room.rect.center
                )

                return True

        return False

    # --------------------------------------------------
    # ZIEL SETZEN
    # --------------------------------------------------

    def assign_target(self, room: Room, mouse_pos: tuple[float, float]):

        idx = self.data.combat.target_weapon_idx

        if idx is None:
            return False

        assert self.data.player.weapons is not None
        if idx >= len(self.data.player.weapons):
            return False

        weapon = self.data.player.weapons[idx]

        self.data.combat.weapon_targets[idx] = (
            room,
            self.data.combat.start_pos,
            (int(mouse_pos[0]), int(mouse_pos[1])),
        )

        self.data.combat.is_targeting = False

        assert weapon is not None
        if weapon.is_ready():
            self.fire_weapon(
                idx,
                room,
                mouse_pos,
            )

        return True

    # --------------------------------------------------
    # SCHUSS ABFEUERN
    # --------------------------------------------------

    def fire_weapon(
        self,
        weapon_index: int,
        target_room: Room,
        end_pos: tuple[float, float],
    ):

        assert self.data.player.weapons is not None
        if weapon_index >= len(self.data.player.weapons):
            return False
        weapon = self.data.player.weapons[weapon_index]

        assert weapon is not None
        if (
            weapon.ammo_cost > 0
            and self.data.player.missiles < weapon.ammo_cost
        ):

            self.show_message(
                "KEINE RAKETEN MEHR!"
            )

            return False

        if weapon.ammo_cost > 0:
            self.data.player.missiles -= weapon.ammo_cost

        self.data.player.projectiles.append(

            Projectile(

                self.data.combat.start_pos,

                end_pos,

                target_room,

                is_player_shot=True,

                w_type=weapon.w_type,

                shield_pierce=weapon.shield_pierce,

                damage=weapon.damage,
            )
        )

        weapon.reset()

        return True

    # --------------------------------------------------
    # AUTOFIRE
    # --------------------------------------------------

    def handle_autofire(self):

        weapon_room = self.data.player.ship.rooms[1]

        assert self.data.player.weapons is not None
        for idx, weapon in enumerate(
            self.data.player.weapons
        ):

            if not weapon.is_ready():
                continue

            if idx not in self.data.combat.weapon_targets:
                continue

            (
                target_room,
                _,
                end_pos,
            ) = self.data.combat.weapon_targets[idx]

            if (
                target_room
                not in self.data.enemy.ship.rooms
            ):
                continue

            if (
                weapon.ammo_cost > 0
                and self.data.player.missiles
                < weapon.ammo_cost
            ):

                self.show_message(
                    "KEINE RAKETEN MEHR!"
                )

                continue

            if weapon.ammo_cost > 0:
                self.data.player.missiles -= (
                    weapon.ammo_cost
                )

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

    # --------------------------------------------------
    # ZIEL ENTFERNEN
    # --------------------------------------------------

    def remove_target(self, mx: float, my: float):

        for idx in list(
            self.data.combat.weapon_targets.keys()
        ):

            _, _, end_pos = (
                self.data.combat.weapon_targets[idx]
            )

            if (
                (mx - end_pos[0]) ** 2
                + (my - end_pos[1]) ** 2
            ) <= 30 ** 2:

                del self.data.combat.weapon_targets[idx]

                return True

        return False

    # --------------------------------------------------
    # AUTOFIRE
    # --------------------------------------------------

    def toggle_autofire(self):

        self.data.combat.autofire_enabled = (
            not self.data.combat.autofire_enabled
        )

    # --------------------------------------------------
    # RESET
    # --------------------------------------------------

    def clear_targets(self):

        self.data.combat.weapon_targets.clear()

        self.data.combat.is_targeting = False

        self.data.combat.target_weapon_idx = None

    # --------------------------------------------------
    # HILFSMETHODEN
    # --------------------------------------------------

    def show_message(self, text: str):

        self.data.combat.msg = text

        self.data.combat.msg_timer = 1.5
