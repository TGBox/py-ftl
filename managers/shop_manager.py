import pygame

from classes.Crew import Crew
from classes.GameData import GameData
from classes.Weapon import Weapon
from settings import *


class ShopManager:

    def __init__(self, data: GameData):
        self.data = data

        self.btn_repair = pygame.Rect(200, 140, 500, 38)
        self.btn_fuel = pygame.Rect(200, 185, 500, 38)
        self.btn_missiles = pygame.Rect(200, 230, 500, 38)
        self.btn_upgrade_reactor = pygame.Rect(200, 275, 500, 38)
        self.btn_buy_crew = pygame.Rect(200, 320, 500, 38)
        self.btn_buy_weapon = pygame.Rect(200, 365, 500, 38)
        self.btn_leave_shop = pygame.Rect(200, 420, 500, 38)

    def handle_click(self, mx: float, my: float):

        if self.btn_repair.collidepoint(mx, my):
            self.buy_repair()

        elif self.btn_fuel.collidepoint(mx, my):
            self.buy_fuel()

        elif self.btn_missiles.collidepoint(mx, my):
            self.buy_missiles()

        elif self.btn_upgrade_reactor.collidepoint(mx, my):
            self.upgrade_reactor()

        elif self.btn_buy_crew.collidepoint(mx, my):
            self.buy_crew()

        elif self.btn_buy_weapon.collidepoint(mx, my):
            self.buy_weapon()

        elif self.btn_leave_shop.collidepoint(mx, my):
            self.leave_shop()

    def buy_repair(self):

        if self.data.player.scrap < 2:
            return

        if self.data.player.ship.hp >= self.data.player.ship.max_hp:
            return

        self.data.player.scrap -= 2
        self.data.player.ship.hp += 1

    def buy_fuel(self):

        if self.data.player.scrap < 3:
            return

        self.data.player.scrap -= 3
        self.data.player.fuel += 1

    def buy_missiles(self):

        if self.data.player.scrap < 6:
            return

        self.data.player.scrap -= 6
        self.data.player.missiles += 3

    def upgrade_reactor(self):

        if self.data.player.scrap < 15:
            return

        self.data.player.scrap -= 15

        self.data.player.reactor.total_power += 1
        self.data.player.reactor.available_power += 1

    def buy_crew(self):
        import random
        max_c = getattr(self.data.player.ship, "max_crew", 4)
        if self.data.player.scrap < 25 or len(self.data.player.crew) >= max_c:
            return

        self.data.player.scrap -= 25
        spawn_room = self.data.player.ship.rooms[0]
        species = random.choice(["Mensch", "Engi", "Mantis"])
        c_num = len(self.data.player.crew) + 1

        self.data.player.crew.append(
            Crew(
                spawn_room.rect.centerx,
                spawn_room.rect.centery,
                name=f"Crew {c_num}",
                species=species,
            )
        )


    def buy_weapon(self):
        import random
        from classes.Weapon import Weapon

        cost = 40
        if self.data.player.scrap < cost:
            self.data.combat.msg = "NICHT GENUG SCRAP!"
            self.data.combat.msg_timer = 1.5
            return

        weapon_pool = [
            {"name": "Schwerer Laser", "charge_time": 3.5, "w_type": "LASER", "shield_pierce": 0, "damage": 45.0, "ammo_cost": 0},
            {"name": "Artemis Rakete", "charge_time": 4.0, "w_type": "MISSILE", "shield_pierce": 1, "damage": 40.0, "ammo_cost": 1},
            {"name": "Pike Strahl", "charge_time": 5.0, "w_type": "BEAM", "shield_pierce": 1, "damage": 30.0, "ammo_cost": 0},
        ]
        chosen = random.choice(weapon_pool)
        max_slots = getattr(self.data.player.ship, "max_weapons", 3)

        # Freier Slot vorhanden
        if len(self.data.player.weapons) < max_slots:
            self.data.player.scrap -= cost
            self.data.player.weapons.append(
                Weapon(
                    chosen["name"],
                    charge_time=chosen["charge_time"],
                    w_type=chosen["w_type"],
                    shield_pierce=chosen["shield_pierce"],
                    damage=chosen["damage"],
                    ammo_cost=chosen["ammo_cost"],
                )
            )
            self.data.combat.msg = f"Gekauft: {chosen['name']}!"
            self.data.combat.msg_timer = 2.0
            return

        # Keine freien Slots -> WAFFEN-FUSION!
        matching_weapon = None
        for w in self.data.player.weapons:
            if w.w_type == chosen["w_type"]:
                matching_weapon = w
                break

        if matching_weapon:
            if matching_weapon.level < 5:
                self.data.player.scrap -= cost
                matching_weapon.upgrade()
                self.data.combat.msg = f"WAFFEN-FUSION! {matching_weapon.name} (Stufe {matching_weapon.level}/5)!"
                self.data.combat.msg_timer = 3.0
            else:
                self.data.combat.msg = f"MAXIMALES FUSION-LEVEL (MK V) FÜR {matching_weapon.w_type.capitalize()} ERREICHT!"
                self.data.combat.msg_timer = 2.5
        else:
            self.data.combat.msg = "KEIN SLOT FREI (Kein gleicher Waffentyp zur Fusion)!"
            self.data.combat.msg_timer = 2.0

    def leave_shop(self):

        self.data.current_state = STATE_MAP