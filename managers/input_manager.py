#import pygame
#
#from settings import *
#
#
#for event in pygame.event.get():
#    if event.type == pygame.QUIT:
#      running = False
#
#    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
#      paused = not paused
#
#    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#      mx, my = pygame.mouse.get_pos()
#
#      if current_state == STATE_MAP and star_map.current_node is not None:  #[cite: 1, 12]
#        print("STATE:", current_state)
#        print("CURRENT:", star_map.current_node.id)
#
#        for node in star_map.current_node.connections:
#            dist = math.hypot(mx - node.x, my - node.y)
#
#            if dist > 18:
#                continue
#
#            if fuel <= 0:
#                print("NO FUEL")
#                break
#
#            fuel -= 1
#            star_map.current_node = node
#            node.visited = True
#
#            if node.event_type == "EXIT":  #[cite: 6]
#              if star_map.sector == 3:  #[cite: 12]
#                current_enemy = copy.deepcopy(ENEMY_BOSS)  #[cite: 1, 11]
#                for r in current_enemy.rooms:
#                  r.current_power = 1
#                print(f"{current_state} -> {STATE_COMBAT}")
#                current_state = STATE_COMBAT  #[cite: 1]
#              else:
#                star_map.sector += 1  #[cite: 12]
#                print(f"Neuer Sektor {star_map.sector}")
#                star_map.generate_map()  #[cite: 12]
#                print("CURRENT", star_map.current_node.id)
#                for n in star_map.current_node.connections:
#                    print("NEXT", n.id, n.x, n.y)
#              scrap += 10
#            elif node.event_type == "SHOP":  #[cite: 6]
#              current_state = STATE_SHOP  #[cite: 1]
#            else:
#              add_scrap, add_fuel = event_mgr.trigger_event(
#                  node.event_type
#              )  #[cite: 5, 6]
#              scrap += add_scrap
#              fuel += add_fuel
#              current_state = STATE_EVENT  #[cite: 1]
#            break
#
#      elif current_state == STATE_SHOP:
#        if btn_repair.collidepoint(mx, my):
#          if scrap >= 2 and player_ship.hp < player_ship.max_hp:
#            scrap -= 2
#            player_ship.hp += 1
#        elif btn_fuel.collidepoint(mx, my):
#          if scrap >= 3:
#            scrap -= 3
#            fuel += 1
#        elif btn_missiles.collidepoint(mx, my):
#          if scrap >= 6:
#            scrap -= 6
#            missiles += 3
#        elif btn_upgrade_reactor.collidepoint(mx, my):
#          if scrap >= 15:
#            scrap -= 15
#            reactor.total_power += 1  #[cite: 8]
#            reactor.available_power += 1  #[cite: 8]
#        elif btn_buy_crew.collidepoint(mx, my):
#          if scrap >= 25:
#            scrap -= 25
#            # Platziere das neue Crew-Mitglied direkt im Zentrum des ersten Schiffraums (z.B. der Piloten-Kabine)
#            spawn_room = player_ship.rooms[0]
#            crew_members.append(Crew(spawn_room.rect.centerx, spawn_room.rect.centery))
#        elif btn_buy_weapon.collidepoint(mx, my):
#          if scrap >= 45 and len(player_weapons) < 3:
#            scrap -= 45
#            player_weapons.append(
#                Weapon(
#                    "Pike Strahl",
#                    charge_time=5.0,
#                    w_type="BEAM",
#                    shield_pierce=1,
#                    damage=25.0,
#                )
#            )  #[cite: 1, 13]
#        elif btn_leave_shop.collidepoint(mx, my):
#          print(f"{current_state} -> {STATE_MAP}")
#          current_state = STATE_MAP  #[cite: 1]
#
#      elif current_state == STATE_EVENT:
#        print("EVENT TYPE:", event_mgr.current_event_type)
#        if event_mgr.current_event_type == "COMBAT":  #[cite: 5]
#          current_enemy = copy.deepcopy(ENEMY_SCOUT)  #[cite: 1, 11]
#          for r in current_enemy.rooms:
#            r.current_power = 1
#          print(f"{current_state} -> {STATE_COMBAT}")
#          current_state = STATE_COMBAT  #[cite: 1]
#        else:
#          print(f"{current_state} -> {STATE_MAP}")
#          current_state = STATE_MAP  #[cite: 1]
#
#      elif current_state == STATE_COMBAT:
#        event_mgr.current_event_type = None
#        if btn_autofire.collidepoint(mx, my):
#          autofire_enabled = not autofire_enabled
#        else:
#          if is_targeting:
#            for e_room in current_enemy.rooms:
#              if e_room.rect.collidepoint(mx, my):
#                if targeting_weapon_idx is not None:
#                  w = player_weapons[targeting_weapon_idx]
#                  # Schusslinie permanent für diese Waffe speichern
#                  weapon_targets[targeting_weapon_idx] = (
#                      e_room,
#                      targeting_start_pos,
#                      (mx, my),
#                  )
#
#                  if w.is_ready():
#                    if w.ammo_cost > 0 and missiles < w.ammo_cost:
#                      combat_msg = "KEINE RAKETEN MEHR!"
#                      combat_msg_timer = 1.5
#                    else:
#                      if w.ammo_cost > 0:
#                        missiles -= w.ammo_cost
#                      projectiles.append(
#                          Projectile(
#                              targeting_start_pos,
#                              (mx, my),
#                              e_room,
#                              is_player_shot=True,
#                              w_type=w.w_type,
#                              shield_pierce=w.shield_pierce,
#                              damage=w.damage,
#                          )
#                      )  #[cite: 1, 7]
#                      w.reset()  #[cite: 13]
#                is_targeting = False
#                break
#            is_targeting = False
#          else:
#            # Prüfen, ob direkt auf ein Waffen-UI-Element geklickt wurde, um zu zielen
#            weapon_room = player_ship.rooms[1]
#            clicked_weapon_idx = None
#            for idx, w in enumerate(player_weapons):
#              bar_x = 30 + idx * 115
#              bar_rect = pygame.Rect(bar_x, 335, 105, 15)
#              if bar_rect.collidepoint(mx, my) or weapon_room.rect.collidepoint(
#                  mx, my
#              ):
#                clicked_weapon_idx = idx
#                break
#
#            if clicked_weapon_idx is not None and player_weapons[clicked_weapon_idx].is_ready():
#              is_targeting = True
#              targeting_weapon_idx = clicked_weapon_idx
#              targeting_start_pos = weapon_room.rect.center
#
#          clicked_crew = False
#          for c in crew_members:
#            if math.hypot(mx - c.x, my - c.y) <= c.radius:  #[cite: 4]
#              for other_c in crew_members:
#                other_c.selected = False  #[cite: 4]
#              c.selected = True  #[cite: 4]
#              clicked_crew = True
#              break
#
#          if not clicked_crew and not is_targeting:
#            has_selected = any(c.selected for c in crew_members)  #[cite: 4]
#            for room in player_ship.rooms:
#              if room.rect.collidepoint(mx, my):
#                if has_selected:
#                  for c in crew_members:
#                    if c.selected:
#                      c.target_pos = (mx, my)  #[cite: 4]
#                else:
#                  room.add_power(reactor)  #[cite: 8, 9]
#
#      elif current_state in (STATE_GAME_OVER, STATE_VICTORY):
#        player_ship = copy.deepcopy(PLAYER_SHIP)  #[cite: 11]
#        star_map.sector = 1  #[cite: 12]
#        star_map.generate_map()  #[cite: 12]
#        fuel, scrap, missiles = 5, 20, 6
#        weapon_targets.clear()
#        print(f"{current_state} -> {STATE_MAP}")
#        current_state = STATE_MAP  #[cite: 1]
#
#    elif (
#        event.type == pygame.MOUSEBUTTONDOWN
#        and event.button == 3
#        and current_state == STATE_COMBAT
#    ):
#      mx, my = pygame.mouse.get_pos()
#      # Rechtsklick zum Löschen einer gezogenen Schusslinie oder Entfernen von Reaktor-Power
#      line_removed = False
#      for idx in list(weapon_targets.keys()):
#        _, start_p, end_p = weapon_targets[idx]
#        # Einfacher Check, ob man in die Nähe der Endposition (Zielraum) geklickt hat
#        if math.hypot(mx - end_p[0], my - end_p[1]) <= 30:
#          del weapon_targets[idx]
#          line_removed = True
#          break
#
#      if not line_removed:
#        has_selected = False
#        for c in crew_members:
#          if c.selected:
#            c.selected = False
#            has_selected = True
#
#        if not has_selected:
#          for room in player_ship.rooms:
#            if room.rect.collidepoint(mx, my):
#              room.remove_power(reactor)  #[cite: 8, 9]

import math

import pygame

from classes.GameData import GameData
from managers.map_manager import MapManager
from managers.shop_manager import ShopManager
from settings import *


class InputManager:

    def __init__(self, data: GameData, shop_manager: ShopManager, map_manager: MapManager):
        self.data = data
        self.shop_manager = shop_manager
        self.map_manager = map_manager

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

        if self.data.current_state == STATE_MAP:
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

        current_node = self.data.star_map.current_node

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
        _mx, _my = pygame.mouse.get_pos()           
    def handle_event_click(self):
        self.map_manager.continue_event()       
    def handle_combat_click(self, event: pygame.event.Event):
        _mx, _my = pygame.mouse.get_pos()     
    def restart_game(self):

        self.map_manager.restart_game()        
    def remove_weapon_target(self, mx: float, my: float):
        pass          
    def deselect_crew(self, event: pygame.event.Event):
        _mx, _my = pygame.mouse.get_pos()     
    def remove_room_power(self, mx: float, my: float):
        pass 
    
    # --------------------------------------------------
    # HILFSMETHODEN
    # --------------------------------------------------

    def show_message(self, text: str):

        self.data.combat_msg = text

        self.data.combat_msg_timer = 1.5