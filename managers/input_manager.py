import math
import pygame

from classes.GameData import GameData
from classes.Projectile import Projectile
from managers.map_manager import MapManager
from managers.shop_manager import ShopManager
from managers.weapon_manager import WeaponManager
from settings import *
from utils import calculate_event_layout


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

    def _logical_mouse_pos(self, pos: tuple[int, int] | None = None) -> tuple[int, int]:
        """Convert raw screen mouse position to logical 900x600 coordinates."""
        if pos is not None:
            raw_mx, raw_my = pos
        else:
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
            elif event.key in (pygame.K_k, pygame.K_1):
                if combat_mgr: combat_mgr.toggle_combat_drone()
            elif event.key in (pygame.K_d, pygame.K_2):
                if combat_mgr: combat_mgr.toggle_repair_drone()
            elif event.key in (pygame.K_f, pygame.K_3):
                if combat_mgr: combat_mgr.toggle_defense_drone()
            elif event.key in (pygame.K_e, pygame.K_4):
                if combat_mgr: combat_mgr.toggle_shield_charger()
            elif event.key in (pygame.K_p, pygame.K_5):
                if combat_mgr: combat_mgr.toggle_anti_personnel()
            elif event.key == pygame.K_g:
                selected = [c for c in self.data.player.crew if c.selected]
                if selected:
                    for c in selected:
                        c.activate_ability(self.data, combat_mgr)
                elif self.data.player.crew:
                    self.data.player.crew[0].activate_ability(self.data, combat_mgr)

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
        elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
            if self.sound:
                self.sound.master_volume = min(1.0, round(self.sound.master_volume + 0.1, 2))
                self.show_message(f"LAUTSTÄRKE: {int(self.sound.master_volume * 100)}%")
        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            if self.sound:
                self.sound.master_volume = max(0.0, round(self.sound.master_volume - 0.1, 2))
                self.show_message(f"LAUTSTÄRKE: {int(self.sound.master_volume * 100)}%")
        elif event.key == pygame.K_m and self.data.player.active_rename_idx is None:
            if self.sound:
                muted = not self.sound.music_enabled
                self.sound.toggle_music()
                self.show_message("MUSIK STUMM" if not muted else "MUSIK AN")
        elif event.key == pygame.K_s and (self.data.paused or getattr(self.data, "show_pause_menu", False) or self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY)):
            self.data.show_slot_modal = True
            self.data.slot_modal_mode = "SAVE"
            if self.sound: self.sound.play("click")
        elif event.key == pygame.K_l:
            from managers.save_manager import SaveManager
            if SaveManager.has_any_savegame():
                self.data.show_slot_modal = True
                self.data.slot_modal_mode = "LOAD"
                if self.sound: self.sound.play("click")

    def handle_left_click(self, event: pygame.event.Event):

        mx, my = self._logical_mouse_pos(getattr(event, "pos", None))        # 1. 3 Save Slots Modal Interaction
        if getattr(self.data, "show_slot_modal", False):
            from managers.save_manager import SaveManager
            mode = getattr(self.data, "slot_modal_mode", "SAVE")

            btn_slot_1 = pygame.Rect(505, 150, 180, 42)
            btn_slot_2 = pygame.Rect(505, 268, 180, 42)
            btn_slot_3 = pygame.Rect(505, 386, 180, 42)
            btn_close = pygame.Rect(350, 475, 200, 42)

            if btn_close.collidepoint(mx, my):
                self.data.show_slot_modal = False
                if self.sound: self.sound.play("click")
                return

            slots = [(1, btn_slot_1), (2, btn_slot_2), (3, btn_slot_3)]
            for slot_num, btn in slots:
                if btn.collidepoint(mx, my):
                    if mode == "SAVE":
                        if SaveManager.save_game(self.data, slot=slot_num):
                            self.sound.play("click") if self.sound else None
                        self.data.show_slot_modal = False
                    elif mode == "LOAD":
                        if SaveManager.has_savegame(slot_num):
                            if SaveManager.load_game(self.data, slot=slot_num):
                                self.sound.play("jump") if self.sound else None
                                self.data.show_pause_menu = False
                                self.data.show_slot_modal = False
                    return
            return

        # 2. Hilfe Overlay Modal Interaktion
        if getattr(self.data, "show_help_overlay", False):
            btn_close = pygame.Rect(320, 440, 220, 38)
            if btn_close.collidepoint(mx, my) or not pygame.Rect(120, 50, 660, 440).collidepoint(mx, my):
                self.data.show_help_overlay = False
                if self.sound: self.sound.play("click")
            return

        # 3. Pause-Menü Modal Interaktion
        if getattr(self.data, "show_pause_menu", False) and self.data.current_state != STATE_OPTIONS:
            btn_pause_resume = pygame.Rect(300, 160, 300, 42)
            btn_pause_save = pygame.Rect(300, 215, 300, 42)
            btn_pause_load = pygame.Rect(300, 270, 300, 42)
            btn_pause_options = pygame.Rect(300, 325, 300, 42)
            btn_pause_main_menu = pygame.Rect(300, 380, 300, 42)

            if btn_pause_resume.collidepoint(mx, my):
                self.data.show_pause_menu = False
                if self.sound: self.sound.play("click")
            elif btn_pause_save.collidepoint(mx, my):
                self.data.show_slot_modal = True
                self.data.slot_modal_mode = "SAVE"
                if self.sound: self.sound.play("click")
            elif btn_pause_load.collidepoint(mx, my):
                self.data.show_slot_modal = True
                self.data.slot_modal_mode = "LOAD"
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

        # 4. Crew-Menü Modal Interaktion
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

        # 5. Optionen Bildschirm
        if self.data.current_state == STATE_OPTIONS:
            btn_toggle_fullscreen = pygame.Rect(210, 105, 480, 36)
            btn_res_toggle = pygame.Rect(210, 148, 480, 36)
            btn_audio_toggle = pygame.Rect(210, 191, 480, 36)

            btn_master_down = pygame.Rect(452, 235, 34, 30)
            btn_master_up = pygame.Rect(648, 235, 34, 30)

            btn_music_down = pygame.Rect(452, 273, 34, 30)
            btn_music_up = pygame.Rect(648, 273, 34, 30)

            btn_sfx_down = pygame.Rect(452, 311, 34, 30)
            btn_sfx_up = pygame.Rect(648, 311, 34, 30)

            btn_autosave_toggle = pygame.Rect(210, 350, 480, 34)
            btn_achievements_menu = pygame.Rect(210, 390, 480, 34)
            btn_close_options = pygame.Rect(350, 460, 200, 40)

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
            elif btn_master_down.collidepoint(mx, my):
                if self.sound:
                    self.sound.master_volume = max(0.0, round(self.sound.master_volume - 0.1, 2))
                    self.sound.play("click")
            elif btn_master_up.collidepoint(mx, my):
                if self.sound:
                    self.sound.master_volume = min(2.0, round(self.sound.master_volume + 0.1, 2))
                    self.sound.play("click")
            elif btn_music_down.collidepoint(mx, my):
                if self.sound:
                    self.sound.music_volume = max(0.0, round(self.sound.music_volume - 0.1, 2))
                    self.sound.play("click")
            elif btn_music_up.collidepoint(mx, my):
                if self.sound:
                    self.sound.music_volume = min(2.0, round(self.sound.music_volume + 0.1, 2))
                    self.sound.play("click")
            elif btn_sfx_down.collidepoint(mx, my):
                if self.sound:
                    self.sound.sfx_volume = max(0.0, round(self.sound.sfx_volume - 0.1, 2))
                    self.sound.play("click")
            elif btn_sfx_up.collidepoint(mx, my):
                if self.sound:
                    self.sound.sfx_volume = min(1.0, round(self.sound.sfx_volume + 0.1, 2))
                    self.sound.play("click")
            elif btn_autosave_toggle.collidepoint(mx, my):
                self.data.auto_save_enabled = not getattr(self.data, "auto_save_enabled", False)
                if self.sound:
                    self.sound.play("click")
            elif btn_achievements_menu.collidepoint(mx, my):
                self.data.current_state = STATE_ACHIEVEMENTS
                if self.sound:
                    self.sound.play("click")
            elif btn_close_options.collidepoint(mx, my):
                if self.sound:
                    self.sound.play("click")
                if getattr(self.data, "show_pause_menu", False) or self.data.paused:
                    self.data.current_state = STATE_MAP
                else:
                    self.data.current_state = STATE_MAIN_MENU
            return

        # 6. Achievements Bildschirm
        if self.data.current_state == STATE_ACHIEVEMENTS:
            categories = ["ALLE", "KAMPF", "CREW", "SCHIFF", "ERKUNDUNG"]
            for idx, cat in enumerate(categories):
                btn_tab = pygame.Rect(55 + idx * 158, 82, 150, 28)
                if btn_tab.collidepoint(mx, my):
                    self.data.achievement_category_filter = cat
                    self.data.achievement_page = 0
                    if self.sound: self.sound.play("click")
                    return

            btn_prev = pygame.Rect(180, 492, 120, 36)
            btn_next = pygame.Rect(600, 492, 120, 36)
            btn_close = pygame.Rect(340, 532, 220, 38)

            if btn_prev.collidepoint(mx, my):
                cur_p = getattr(self.data, "achievement_page", 0)
                self.data.achievement_page = max(0, cur_p - 1)
                if self.sound: self.sound.play("click")
                return
            elif btn_next.collidepoint(mx, my):
                cur_p = getattr(self.data, "achievement_page", 0)
                self.data.achievement_page = cur_p + 1
                if self.sound: self.sound.play("click")
                return
            elif btn_close.collidepoint(mx, my):
                if self.sound: self.sound.play("click")
                self.data.current_state = STATE_OPTIONS
                return
            return

        # 7. Shop Modal State
        if self.data.current_state == STATE_SHOP:
            self.shop_manager.handle_click(mx, my)
            return

        # 8. Main Menu State
        if self.data.current_state == STATE_MAIN_MENU:
            import copy
            from classes.ShipModel import SHIP_BLUEPRINTS, apply_starting_setup_for_ship
            from managers.save_manager import SaveManager

            unlocked = getattr(self.data.player, "unlocked_ships", ["Kestrel"])

            col_x = [40, 250, 460, 670]
            row_y = [82, 226]
            ship_list = list(SHIP_BLUEPRINTS.keys())

            for idx, name in enumerate(ship_list):
                r_idx = idx // 4
                c_idx = idx % 4
                if r_idx < 2:
                    card_btn = pygame.Rect(col_x[c_idx], row_y[r_idx], 195, 138)
                    if card_btn.collidepoint(mx, my) and name in unlocked:
                        self.data.player.ship = copy.deepcopy(SHIP_BLUEPRINTS[name])
                        apply_starting_setup_for_ship(self.data.player, name)
                        if self.sound:
                            self.sound.play("click")
                        return

            btn_start = pygame.Rect(40, 532, 195, 42)
            btn_continue_game = pygame.Rect(250, 532, 195, 42)
            btn_options = pygame.Rect(460, 532, 195, 42)
            btn_quit = pygame.Rect(670, 532, 195, 42)

            if btn_options.collidepoint(mx, my):
                self.data.current_state = STATE_OPTIONS
                if self.sound:
                    self.sound.play("click")
            elif btn_start.collidepoint(mx, my):
                self.data.current_state = STATE_MAP
                if self.sound:
                    self.sound.play("jump")
            elif SaveManager.has_any_savegame() and btn_continue_game.collidepoint(mx, my):
                self.data.show_slot_modal = True
                self.data.slot_modal_mode = "LOAD"
                if self.sound:
                    self.sound.play("click")
            elif btn_quit.collidepoint(mx, my):
                self.data.running = False
                if self.sound:
                    self.sound.play("click")
            return

        # 9. Top Action Bar & Door Controls (ONLY evaluated when NO modal/menu/shop is open)
        if self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY):
            btn_crew_toggle = pygame.Rect(750, 8, 130, 26)
            btn_open_all = pygame.Rect(750, 38, 130, 26)
            btn_close_all = pygame.Rect(750, 68, 130, 26)
            btn_vent = pygame.Rect(750, 98, 130, 26)
            btn_help_toggle = pygame.Rect(750, 128, 130, 26)

            if btn_help_toggle.collidepoint(mx, my):
                self.data.show_help_overlay = not getattr(self.data, "show_help_overlay", False)
                if self.sound: self.sound.play("click")
                return
            elif btn_crew_toggle.collidepoint(mx, my):
                self.data.player.show_crew_menu = not getattr(self.data.player, "show_crew_menu", False)
                return
            elif btn_open_all.collidepoint(mx, my):
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

        # 10. State-specific clicks (Map, Event, Combat, Training)
        if self.data.current_state == STATE_MAP:
            self.handle_map_click(mx, my)

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
        mx, my = self._logical_mouse_pos(getattr(event, "pos", None))
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

        ev_text = ev_mgr.current_event_text
        res_text = getattr(ev_mgr, "result_text", "")
        choices = ev_mgr.choices

        font = pygame.font.SysFont(None, 24)
        layout = calculate_event_layout(ev_text, res_text, choices, font)
        box_rect = layout["box_rect"]

        # Wenn result_text angezeigt wird oder keine Choices da sind: Klick im Fenster schließt Event ab
        if ev_mgr.result_text or not choices:
            cont_btn = layout.get("cont_btn")
            if (cont_btn and cont_btn.collidepoint(mx, my)) or box_rect.collidepoint(mx, my):
                self.map_manager.continue_event()
            return

        for idx, choice in enumerate(choices):
            if idx < len(layout["choice_rects"]):
                btn_rect = layout["choice_rects"][idx]
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
