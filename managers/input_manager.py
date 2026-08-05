import math
import pygame

from classes.GameData import GameData
from classes.Projectile import Projectile
from managers.map_manager import MapManager
from managers.shop_manager import ShopManager
from managers.weapon_manager import WeaponManager
from settings import *


class InputManager:

    def __init__(
        self,
        data: GameData,
        shop_manager: ShopManager,
        map_manager: MapManager,
        weapon_manager: WeaponManager | None = None,
    ):
        self.data = data
        self.shop_manager = shop_manager
        self.map_manager = map_manager
        self.weapon_manager = weapon_manager or WeaponManager(data)

    def update(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.data.running = False

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.handle_left_click(event)

                elif event.button == 3:
                    self.handle_right_click(event)

    def handle_keydown(self, event: pygame.event.Event):
        if event.key == pygame.K_SPACE:
            self.data.paused = not self.data.paused

    def handle_left_click(self, event: pygame.event.Event):

        mx, my = pygame.mouse.get_pos()

        if self.data.current_state == STATE_MAIN_MENU:
            btn_start = pygame.Rect(SCREEN_WIDTH // 2 - 100, 350, 200, 50)
            if btn_start.collidepoint(mx, my):
                self.restart_game()

        elif self.data.current_state == STATE_MAP:
            self.handle_map_click(mx, my)

        elif self.data.current_state == STATE_SHOP:
            self.shop_manager.handle_click(mx, my)

        elif self.data.current_state == STATE_EVENT:
            self.handle_event_click()

        elif self.data.current_state == STATE_COMBAT:
            self.handle_combat_click(event)

        elif self.data.current_state in (STATE_GAME_OVER, STATE_VICTORY):
            self.restart_game()

    def handle_right_click(self, event: pygame.event.Event):
        if self.data.current_state != STATE_COMBAT:
            return
        mx, my = pygame.mouse.get_pos()
        if self.remove_weapon_target(mx, my):
            return
        if self.deselect_crew(event):
            return
        self.remove_room_power(mx, my)

    def handle_map_click(self, mx: float, my: float):

        current_node = self.data.world.star_map.current_node

        if current_node is None:
            return

        for node in current_node.connections:

            dist = math.hypot(
                mx - node.x,
                my - node.y,
            )

            if dist <= 18:
                self.map_manager.travel_to_node(node)
                break

    def handle_shop_click(self, event: pygame.event.Event):
        mx, my = pygame.mouse.get_pos()
        self.shop_manager.handle_click(mx, my)

    def handle_event_click(self):
        mx, my = pygame.mouse.get_pos()
        choices = self.data.world.event_manager.choices
        if not choices:
            self.map_manager.continue_event()
            return

        for idx, choice in enumerate(choices):
            btn_rect = pygame.Rect(180, 260 + idx * 50, 540, 36)
            if btn_rect.collidepoint(mx, my):
                action = choice.get("action", "")
                self.map_manager.handle_choice(action, choice)
                return

        if len(choices) == 1:
            action = choices[0].get("action", "")
            self.map_manager.handle_choice(action, choices[0])


    def handle_combat_click(self, event: pygame.event.Event):
        mx, my = pygame.mouse.get_pos()
        self.data.world.event_manager.current_event_type = None

        btn_autofire = pygame.Rect(730, 310, 140, 30)
        if btn_autofire.collidepoint(mx, my):
            self.data.combat.autofire_enabled = not self.data.combat.autofire_enabled
            return

        if self.data.combat.is_targeting:
            for e_room in self.data.enemy.ship.rooms:
                if e_room.rect.collidepoint(mx, my):
                    idx = self.data.combat.target_weapon_idx
                    if idx is not None and idx < len(self.data.player.weapons):
                        w = self.data.player.weapons[idx]
                        self.data.combat.weapon_targets[idx] = (
                            e_room,
                            self.data.combat.start_pos,
                            (mx, my),
                        )
                        if w.is_ready():
                            if w.ammo_cost > 0 and self.data.player.missiles < w.ammo_cost:
                                self.show_message("KEINE RAKETEN MEHR!")
                            else:
                                if w.ammo_cost > 0:
                                    self.data.player.missiles -= w.ammo_cost
                                self.data.player.projectiles.append(
                                    Projectile(
                                        self.data.combat.start_pos,
                                        (mx, my),
                                        e_room,
                                        is_player_shot=True,
                                        w_type=w.w_type,
                                        shield_pierce=w.shield_pierce,
                                        damage=w.damage,
                                    )
                                )
                                w.reset()
                    break
            self.data.combat.is_targeting = False
            return

        weapon_room = self.data.player.ship.rooms[1]
        clicked_weapon_idx = None
        for idx, w in enumerate(self.data.player.weapons):
            bar_x = 30 + idx * 115
            bar_rect = pygame.Rect(bar_x, 335, 105, 15)
            if bar_rect.collidepoint(mx, my) or weapon_room.rect.collidepoint(mx, my):
                clicked_weapon_idx = idx
                break

        if clicked_weapon_idx is not None and self.data.player.weapons[clicked_weapon_idx].is_ready():
            self.data.combat.is_targeting = True
            self.data.combat.target_weapon_idx = clicked_weapon_idx
            self.data.combat.start_pos = weapon_room.rect.center
            return

        clicked_crew = False
        for c in self.data.player.crew:
            if math.hypot(mx - c.x, my - c.y) <= c.radius:
                for other_c in self.data.player.crew:
                    other_c.selected = False
                c.selected = True
                clicked_crew = True
                break

        if not clicked_crew:
            has_selected = any(c.selected for c in self.data.player.crew)
            for room in self.data.player.ship.rooms:
                if room.rect.collidepoint(mx, my):
                    if has_selected:
                        for c in self.data.player.crew:
                            if c.selected:
                                c.target_pos = (int(mx), int(my))
                    else:
                        room.add_power(self.data.player.reactor)
                    break

    def restart_game(self):
        self.map_manager.restart_game()

    def remove_weapon_target(self, mx: float, my: float) -> bool:
        for idx in list(self.data.combat.weapon_targets.keys()):
            _, _, end_p = self.data.combat.weapon_targets[idx]
            if math.hypot(mx - end_p[0], my - end_p[1]) <= 30:
                del self.data.combat.weapon_targets[idx]
                return True
        return False

    def deselect_crew(self, event: pygame.event.Event) -> bool:
        has_selected = False
        for c in self.data.player.crew:
            if c.selected:
                c.selected = False
                has_selected = True
        return has_selected

    def remove_room_power(self, mx: float, my: float):
        for room in self.data.player.ship.rooms:
            if room.rect.collidepoint(mx, my):
                room.remove_power(self.data.player.reactor)
                break

    # --------------------------------------------------
    # HILFSMETHODEN
    # --------------------------------------------------

    def show_message(self, text: str):
        self.data.combat.msg = text
        self.data.combat.msg_timer = 1.5
