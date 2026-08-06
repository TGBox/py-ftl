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
        self.sound = None   # Set by Game after construction
        self.game = None    # Set by Game after construction

    def _logical_mouse_pos(self) -> tuple[int, int]:
        """Convert raw screen mouse position to logical 900x600 coordinates."""
        raw_mx, raw_my = pygame.mouse.get_pos()
        if self.game and hasattr(self.game, "screen_to_logical"):
            return self.game.screen_to_logical(raw_mx, raw_my)
        return raw_mx, raw_my

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
        if self.data.player.active_rename_idx is not None:
            if event.key == pygame.K_RETURN:
                idx = self.data.player.active_rename_idx
                if 0 <= idx < len(self.data.player.crew):
                    new_name = self.data.player.rename_buffer.strip()
                    if new_name:
                        self.data.player.crew[idx].name = new_name
                self.data.player.active_rename_idx = None
                self.data.player.rename_buffer = ""
            elif event.key == pygame.K_BACKSPACE:
                self.data.player.rename_buffer = self.data.player.rename_buffer[:-1]
            elif event.unicode and len(self.data.player.rename_buffer) < 16:
                self.data.player.rename_buffer += event.unicode
            return

        # Hilfe-Overlay Umschalten (H / F1)
        if event.key in (pygame.K_h, pygame.K_F1):
            self.data.show_help_overlay = not getattr(self.data, "show_help_overlay", False)
            if self.sound: self.sound.play("click")
            return

        combat_mgr = getattr(self.data, "combat_manager", None)
        if self.data.current_state == STATE_COMBAT:
            if event.key == pygame.K_a:
                self.data.combat.autofire_enabled = not self.data.combat.autofire_enabled
            elif event.key == pygame.K_b:
                if getattr(self.data.combat, "teleport_cooldown", 0.0) <= 0:
                    self.data.combat.is_teleport_targeting = not getattr(self.data.combat, "is_teleport_targeting", False)
            elif event.key == pygame.K_r:
                if combat_mgr: combat_mgr.recall_boarding_crew()
            elif event.key == pygame.K_c:
                if combat_mgr: combat_mgr.activate_cloaking()
            elif event.key == pygame.K_k:
                if combat_mgr: combat_mgr.toggle_combat_drone()
            elif event.key == pygame.K_d:
                if combat_mgr: combat_mgr.toggle_repair_drone()

        if self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY):
            if event.key == pygame.K_o:
                self.data.player.ship.open_all_doors()
            elif event.key == pygame.K_v:
                self.data.player.ship.open_airlocks()

        if event.key == pygame.K_SPACE:
            # Taktische Pause umschalten (Spiel-Interaktionen bleiben möglich)
            self.data.paused = not self.data.paused
        elif event.key == pygame.K_ESCAPE:
            # Pause-Menü Modal (ESC)
            if self.data.current_state == STATE_OPTIONS:
                if getattr(self.data, "show_pause_menu", False):
                    self.data.current_state = STATE_MAP
                else:
                    self.data.current_state = STATE_MAIN_MENU
            elif self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY):
                self.data.show_pause_menu = not getattr(self.data, "show_pause_menu", False)
                if self.sound: self.sound.play("click")
        elif event.key == pygame.K_s and (self.data.paused or getattr(self.data, "show_pause_menu", False) or self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY)):
            from managers.save_manager import SaveManager
            if SaveManager.save_game(self.data):
                self.show_message("SPIELSTAND ERFOLGREICH GESPEICHERT!")

    def handle_left_click(self, event: pygame.event.Event):

        mx, my = self._logical_mouse_pos()

        # [?] HILFE Toggle Button Klick
        btn_help_toggle = pygame.Rect(750, 135, 130, 26)
        if btn_help_toggle.collidepoint(mx, my):
            self.data.show_help_overlay = not getattr(self.data, "show_help_overlay", False)
            if self.sound: self.sound.play("click")
            return

        # Pause-Menü Modal Interaktion (wenn ESC-Pausemenü geöffnet ist)
        if getattr(self.data, "show_pause_menu", False) and self.data.current_state != STATE_OPTIONS:
            btn_pause_resume = pygame.Rect(300, 160, 300, 42)
            btn_pause_save = pygame.Rect(300, 215, 300, 42)
            btn_pause_load = pygame.Rect(300, 270, 300, 42)
            btn_pause_options = pygame.Rect(300, 325, 300, 42)
            btn_pause_main_menu = pygame.Rect(300, 380, 300, 42)

            from managers.save_manager import SaveManager

            if btn_pause_resume.collidepoint(mx, my):
                self.data.show_pause_menu = False
                if self.sound: self.sound.play("click")
            elif btn_pause_save.collidepoint(mx, my):
                if SaveManager.save_game(self.data):
                    self.show_message("SPIELSTAND ERFOLGREICH GESPEICHERT!")
                if self.sound: self.sound.play("click")
            elif btn_pause_load.collidepoint(mx, my):
                if SaveManager.load_game(self.data):
                    self.show_message("SPIELSTAND ERFOLGREICH GELADEN!")
                if self.sound: self.sound.play("click")
            elif btn_pause_options.collidepoint(mx, my):
                self.data.current_state = STATE_OPTIONS
                if self.sound: self.sound.play("click")
            elif btn_pause_main_menu.collidepoint(mx, my):
                self.data.show_pause_menu = False
                self.data.paused = False
                self.data.current_state = STATE_MAIN_MENU
                if self.sound: self.sound.play("click")
            return

        # Crew-Menü Toggle & Interaction
        btn_crew_toggle = pygame.Rect(750, 8, 130, 26)
        if self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY) and btn_crew_toggle.collidepoint(mx, my):
            self.data.player.show_crew_menu = not getattr(self.data.player, "show_crew_menu", False)
            return

        # Tür-Steuerung UI Buttons & Tür-Direktklicks
        if self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY):
            btn_open_all = pygame.Rect(750, 38, 130, 26)
            btn_close_all = pygame.Rect(750, 68, 130, 26)
            btn_vent = pygame.Rect(750, 98, 130, 26)
            btn_help_toggle = pygame.Rect(750, 128, 130, 26)

            if btn_help_toggle.collidepoint(mx, my):
                self.data.show_help_overlay = not getattr(self.data, "show_help_overlay", False)
                if self.sound: self.sound.play("click")
                return

            if btn_open_all.collidepoint(mx, my):
                self.data.player.ship.open_all_doors()
                if self.sound: self.sound.play("click")
                return
            elif btn_close_all.collidepoint(mx, my):
                self.data.player.ship.close_all_doors()
                if self.sound: self.sound.play("click")
                return
            elif btn_vent.collidepoint(mx, my):
                self.data.player.ship.open_airlocks()
                if self.sound: self.sound.play("click")
                return

            for d in self.data.player.ship.doors:
                if d.rect.collidepoint(mx, my):
                    d.toggle()
                    if self.sound: self.sound.play("click")
                    return

        if getattr(self.data.player, "show_crew_menu", False):
            close_btn = pygame.Rect(370, 465, 160, 38)
            if close_btn.collidepoint(mx, my):
                self.data.player.show_crew_menu = False
                self.data.player.active_rename_idx = None
                return

            for idx, crew in enumerate(self.data.player.crew):
                card_y = 130 + idx * 75
                rename_btn = pygame.Rect(580, card_y + 15, 130, 35)
                if rename_btn.collidepoint(mx, my):
                    self.data.player.active_rename_idx = idx
                    self.data.player.rename_buffer = crew.name
                    return
            return

        if self.data.current_state == STATE_OPTIONS:
            btn_toggle_fullscreen = pygame.Rect(210, 140, 480, 44)
            btn_res_toggle = pygame.Rect(210, 195, 480, 44)
            btn_audio_toggle = pygame.Rect(220, 250, 460, 44)
            btn_close_options = pygame.Rect(350, 440, 200, 45)
            if btn_toggle_fullscreen.collidepoint(mx, my):
                if self.game:
                    self.game.cycle_display_mode()
                if self.sound:
                    self.sound.play("click")
            elif btn_res_toggle.collidepoint(mx, my):
                if self.game:
                    self.game.cycle_resolution()
                if self.sound:
                    self.sound.play("click")
            elif btn_audio_toggle.collidepoint(mx, my):
                if self.sound:
                    self.sound.toggle()
                    self.sound.play("click")
            elif btn_close_options.collidepoint(mx, my):
                if self.sound:
                    self.sound.play("click")
                if getattr(self.data, "show_pause_menu", False) or self.data.paused:
                    self.data.current_state = STATE_MAP
                else:
                    self.data.current_state = STATE_MAIN_MENU
            return

        if self.data.current_state == STATE_MAIN_MENU:
            btn_kestrel = pygame.Rect(45, 95, 155, 275)
            btn_kreuzer = pygame.Rect(210, 95, 155, 275)
            btn_tarnschiff = pygame.Rect(375, 95, 155, 275)
            btn_zoltan = pygame.Rect(540, 95, 155, 275)
            btn_fed = pygame.Rect(705, 95, 155, 275)

            btn_start = pygame.Rect(45, 395, 185, 44)
            btn_continue_game = pygame.Rect(250, 395, 185, 44)
            btn_options = pygame.Rect(455, 395, 185, 44)
            btn_quit = pygame.Rect(660, 395, 185, 44)

            import copy
            from classes.ShipModel import SHIP_BLUEPRINTS
            from managers.save_manager import SaveManager

            unlocked = getattr(self.data.player, "unlocked_ships", ["Kestrel"])

            if btn_kestrel.collidepoint(mx, my) and "Kestrel" in unlocked:
                self.data.player.ship = copy.deepcopy(SHIP_BLUEPRINTS["Kestrel"])
                if self.sound: self.sound.play("click")
            elif btn_kreuzer.collidepoint(mx, my) and "Kreuzer" in unlocked:
                self.data.player.ship = copy.deepcopy(SHIP_BLUEPRINTS["Kreuzer"])
                if self.sound: self.sound.play("click")
            elif btn_tarnschiff.collidepoint(mx, my) and "Tarnschiff" in unlocked:
                self.data.player.ship = copy.deepcopy(SHIP_BLUEPRINTS["Tarnschiff"])
                if self.sound: self.sound.play("click")
            elif btn_zoltan.collidepoint(mx, my) and "Zoltan-Fregatte" in unlocked:
                self.data.player.ship = copy.deepcopy(SHIP_BLUEPRINTS["Zoltan-Fregatte"])
                if self.sound: self.sound.play("click")
            elif btn_fed.collidepoint(mx, my) and "Federations-Kreuzer" in unlocked:
                self.data.player.ship = copy.deepcopy(SHIP_BLUEPRINTS["Federations-Kreuzer"])
                if self.sound: self.sound.play("click")
            elif btn_options.collidepoint(mx, my):
                self.data.current_state = STATE_OPTIONS
                if self.sound: self.sound.play("click")
            elif btn_start.collidepoint(mx, my):
                self.data.current_state = STATE_MAP
                if self.sound: self.sound.play("jump")
            elif SaveManager.has_savegame() and btn_continue_game.collidepoint(mx, my):
                if SaveManager.load_game(self.data):
                    if self.sound: self.sound.play("jump")
            elif btn_quit.collidepoint(mx, my):
                self.data.running = False
                if self.sound: self.sound.play("click")
            return




        elif self.data.current_state == STATE_MAP:
            self.handle_map_click(mx, my)

        elif self.data.current_state == STATE_SHOP:
            self.shop_manager.handle_click(mx, my)

        elif self.data.current_state == STATE_TRAINING:
            training_mgr = getattr(self.data, "training_manager", None)
            if training_mgr:
                training_mgr.handle_click(mx, my)

        elif self.data.current_state == STATE_EVENT:
            self.handle_event_click()

        elif self.data.current_state == STATE_COMBAT:
            self.handle_combat_click(event)

        elif self.data.current_state in (STATE_GAME_OVER, STATE_VICTORY):
            self.restart_game()
            self.data.current_state = STATE_MAIN_MENU


    def handle_right_click(self, event: pygame.event.Event):
        if self.data.current_state != STATE_COMBAT:
            return
        mx, my = self._logical_mouse_pos()
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
        mx, my = self._logical_mouse_pos()
        self.shop_manager.handle_click(mx, my)

    def handle_event_click(self):
        mx, my = self._logical_mouse_pos()
        ev_mgr = self.data.world.event_manager

        box_rect = pygame.Rect(120, 100, 660, 380)

        # Wenn result_text angezeigt wird: Klick im Fenster schließt Event ab
        if ev_mgr.result_text:
            if box_rect.collidepoint(mx, my):
                self.map_manager.continue_event()
            return

        choices = ev_mgr.choices
        if not choices:
            if box_rect.collidepoint(mx, my):
                self.map_manager.continue_event()
            return

        for idx, choice in enumerate(choices):
            btn_y = 200 + idx * 44
            btn_rect = pygame.Rect(150, btn_y, 600, 38)
            if btn_rect.collidepoint(mx, my):
                action = choice.get("action", "")
                if self.sound: self.sound.play("click")
                self.map_manager.handle_choice(action, choice)
                return



    def handle_combat_click(self, event: pygame.event.Event):
        mx, my = self._logical_mouse_pos()
        self.data.world.event_manager.current_event_type = None

        btn_repair_drone = pygame.Rect(415, 470, 140, 34)
        btn_combat_drone = pygame.Rect(565, 470, 140, 34)
        btn_cloak = pygame.Rect(715, 470, 140, 34)
        btn_recall = pygame.Rect(415, 512, 140, 34)
        btn_teleport = pygame.Rect(565, 512, 140, 34)
        btn_autofire = pygame.Rect(715, 512, 140, 34)

        tp_cd = getattr(self.data.combat, "teleport_cooldown", 0.0)
        combat_mgr = getattr(self.data, "combat_manager", None)

        if btn_autofire.collidepoint(mx, my):
            self.data.combat.autofire_enabled = not self.data.combat.autofire_enabled
            return

        if btn_teleport.collidepoint(mx, my):
            if tp_cd <= 0:
                self.data.combat.is_teleport_targeting = not getattr(self.data.combat, "is_teleport_targeting", False)
                if self.sound: self.sound.play("click")
            else:
                self.show_message(f"TELEPORTER LÄDT NOCH ({int(tp_cd)}s)!")
            return

        if btn_recall.collidepoint(mx, my):
            has_boarders = any(getattr(c, "is_boarding", False) for c in self.data.player.crew)
            if has_boarders:
                if combat_mgr:
                    combat_mgr.recall_boarding_crew()
            else:
                self.show_message("KEINE CREW AUF DEM GEGNERSCHIFF!")
            return

        if btn_cloak.collidepoint(mx, my):
            if combat_mgr:
                combat_mgr.activate_cloaking()
            return

        if btn_combat_drone.collidepoint(mx, my):
            if combat_mgr:
                combat_mgr.toggle_combat_drone()
            return

        if btn_repair_drone.collidepoint(mx, my):
            if combat_mgr:
                combat_mgr.toggle_repair_drone()
            return

        # Teleporter Zielauswahl auf dem Gegnerschiff
        if getattr(self.data.combat, "is_teleport_targeting", False):
            for e_room in self.data.enemy.ship.rooms:
                if e_room.rect.collidepoint(mx, my):
                    if combat_mgr:
                        combat_mgr.teleport_selected_crew_to_room(e_room)
                    break
            self.data.combat.is_teleport_targeting = False
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
            bar_x = 30 + idx * 135
            bar_rect = pygame.Rect(bar_x, 500, 120, 35)
            if bar_rect.collidepoint(mx, my):
                clicked_weapon_idx = idx
                break

        if clicked_weapon_idx is not None and self.data.player.weapons[clicked_weapon_idx].is_ready():
            self.data.combat.is_targeting = True
            self.data.combat.target_weapon_idx = clicked_weapon_idx
            slots = getattr(self.data.player.ship, "weapon_slots", [])
            if slots and clicked_weapon_idx < len(slots):
                self.data.combat.start_pos = slots[clicked_weapon_idx]["pos"]
            else:
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
            if has_selected:
                # Klick auf Gegnerschiff für Bewegung von Enter-Crew
                for e_room in self.data.enemy.ship.rooms:
                    if e_room.rect.collidepoint(mx, my):
                        for c in self.data.player.crew:
                            if c.selected and c.is_boarding:
                                c.target_pos = (int(mx), int(my))
                        return

                # Klick auf eigenes Schiff für Bewegung von normaler Crew
                for room in self.data.player.ship.rooms:
                    if room.rect.collidepoint(mx, my):
                        for c in self.data.player.crew:
                            if c.selected and not c.is_boarding:
                                c.target_pos = (int(mx), int(my))
                        return
            else:
                for room in self.data.player.ship.rooms:
                    if room.rect.collidepoint(mx, my):
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
        self.data.combat.msg_timer = 2.0
        self.data.save_toast_text = text
        self.data.save_toast_timer = 2.5
