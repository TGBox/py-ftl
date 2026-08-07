import random
import pygame

from classes.Crew import Crew
from classes.GameData import GameData
from classes.Weapon import Weapon
from settings import *

WEAPON_CATALOG_MASTER = [
    {"name": "Standard Laser", "charge_time": 3.0, "w_type": "LASER", "shield_pierce": 0, "damage": 25.0, "ammo_cost": 0, "price": 30, "subtype": "STANDARD"},
    {"name": "Schwerer Laser", "charge_time": 3.5, "w_type": "LASER", "shield_pierce": 0, "damage": 45.0, "ammo_cost": 0, "price": 50, "subtype": "HEAVY"},
    {"name": "Burst Laser MK II", "charge_time": 4.0, "w_type": "LASER", "shield_pierce": 0, "damage": 60.0, "ammo_cost": 0, "price": 70, "subtype": "STANDARD"},
    {"name": "Artemis Rakete", "charge_time": 4.0, "w_type": "MISSILE", "shield_pierce": 1, "damage": 40.0, "ammo_cost": 1, "price": 40, "subtype": "STANDARD"},
    {"name": "Pike Strahl", "charge_time": 5.0, "w_type": "BEAM", "shield_pierce": 1, "damage": 35.0, "ammo_cost": 0, "price": 60, "subtype": "STANDARD"},
    {"name": "Ion Blast MK I", "charge_time": 3.0, "w_type": "ION", "shield_pierce": 0, "damage": 10.0, "ammo_cost": 0, "price": 45, "subtype": "STANDARD"},
    {"name": "Bio-Strahl MK I", "charge_time": 4.5, "w_type": "BEAM", "shield_pierce": 0, "damage": 0.0, "ammo_cost": 0, "price": 65, "subtype": "BIO", "crew_damage": 65.0},
    {"name": "Brand-Laser MK I", "charge_time": 3.8, "w_type": "LASER", "shield_pierce": 0, "damage": 15.0, "ammo_cost": 0, "price": 55, "subtype": "FIRE", "fire_chance": 0.75},
    {"name": "Betäubungs-Ion MK I", "charge_time": 3.0, "w_type": "ION", "shield_pierce": 0, "damage": 10.0, "ammo_cost": 0, "price": 50, "subtype": "STUN", "stun_duration": 6.0},
    {"name": "Schwerer Hüllenbrecher", "charge_time": 4.2, "w_type": "LASER", "shield_pierce": 0, "damage": 35.0, "ammo_cost": 0, "price": 60, "subtype": "BREACH", "breach_chance": 0.60},
    {"name": "Anti-Materie Kanone", "charge_time": 4.8, "w_type": "MISSILE", "shield_pierce": 1, "damage": 10.0, "ammo_cost": 1, "price": 75, "subtype": "BIO", "crew_damage": 85.0},
    {"name": "Feuer-Bombe", "charge_time": 4.5, "w_type": "BOMB", "shield_pierce": 99, "damage": 0.0, "ammo_cost": 1, "price": 55, "subtype": "FIRE", "fire_chance": 0.90},
    {"name": "Hüllenbruch-Bombe", "charge_time": 5.0, "w_type": "BOMB", "shield_pierce": 99, "damage": 15.0, "ammo_cost": 1, "price": 60, "subtype": "BREACH", "breach_chance": 0.90},
]


AUGMENT_CATALOG_MASTER = [
    {"name": "Waffen-Vorheizer", "type": "AUGMENT", "desc": "Waffen starten zu 100% geladen!", "price": 80},
    {"name": "Schild-Booster", "type": "AUGMENT", "desc": "+30% Schild-Erholung!", "price": 60},
    {"name": "Automatisierte Relais", "type": "AUGMENT", "desc": "Repariert Räume automatisch!", "price": 50},
    {"name": "Sauerstoff-Konverter", "type": "AUGMENT", "desc": "+50% O2-Regeneration!", "price": 40},
    {"name": "Schrott-Arm", "type": "AUGMENT", "desc": "+30% Schrott-Beute!", "price": 55},
]


class ShopManager:

    def __init__(self, data: GameData):
        self.data = data
        self.catalog_stock: list[dict] = []
        self.selecting_slot_item: dict | None = None
        self.layout_swap_mode: bool = False
        self.layout_swap_first_room = None
        self.refresh_catalog()

        # Navigation & Basis-Buttons
        self.btn_repair = pygame.Rect(80, 130, 350, 30)
        self.btn_fuel = pygame.Rect(80, 165, 350, 30)
        self.btn_missiles = pygame.Rect(80, 200, 350, 30)
        self.btn_upgrade_reactor = pygame.Rect(80, 235, 350, 30)
        self.btn_buy_crew = pygame.Rect(80, 270, 350, 30)
        self.btn_edit_layout = pygame.Rect(80, 305, 350, 30)
        self.btn_leave_shop = pygame.Rect(340, 495, 220, 40)

    def refresh_catalog(self):
        w_sample = random.sample(WEAPON_CATALOG_MASTER, min(2, len(WEAPON_CATALOG_MASTER)))
        a_sample = random.sample(AUGMENT_CATALOG_MASTER, min(1, len(AUGMENT_CATALOG_MASTER)))
        self.catalog_stock = w_sample + a_sample
        self.selecting_slot_item = None
        self.layout_swap_mode = False
        self.layout_swap_first_room = None

    def handle_click(self, mx: float, my: float):
        # Falls Layout-Umbau Modal aktiv ist:
        if self.layout_swap_mode:
            self.handle_layout_swap_click(mx, my)
            return

        # Falls Slot-Auswahl Modal aktiv ist:
        if self.selecting_slot_item is not None:
            self.handle_slot_selection_click(mx, my)
            return

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
        elif self.btn_edit_layout.collidepoint(mx, my):
            self.start_layout_swap()
        elif self.btn_leave_shop.collidepoint(mx, my):
            self.leave_shop()

        # Klick auf Waffenkatalog zum Kaufen
        for idx, item in enumerate(self.catalog_stock):
            item_btn = pygame.Rect(470, 130 + idx * 62, 350, 56)
            if item_btn.collidepoint(mx, my):
                if item.get("type") == "AUGMENT":
                    self.buy_augment(item)
                else:
                    self.selecting_slot_item = item
                return

        # Klick auf "Verkaufen" bei eigenen Waffen
        max_slots = getattr(self.data.player.ship, "max_weapons", 3)
        card_w = (740 - (max_slots - 1) * 12) // max_slots
        for idx, w in enumerate(self.data.player.weapons):
            card_x = 80 + idx * (card_w + 12)
            sell_btn = pygame.Rect(card_x + 6, 412, card_w - 12, 22)
            if sell_btn.collidepoint(mx, my):
                self.sell_weapon_at_slot(idx)
                return

    def start_layout_swap(self):
        if self.data.player.scrap < 15:
            self.data.combat.msg = "NICHT GENUG SCRAP FÜR LAYOUT-UMBAU (15 SCRAP BENÖTIGT)!"
            self.data.combat.msg_timer = 2.0
            return
        self.layout_swap_mode = True
        self.layout_swap_first_room = None
        self.data.combat.msg = "LAYOUT-UMBAU: KLICKE AUF DEN ERSTEN RAUM ZUM TAUSCHEN!"
        self.data.combat.msg_timer = 3.0

    def handle_layout_swap_click(self, mx: float, my: float):
        btn_cancel = pygame.Rect(320, 490, 260, 40)
        if btn_cancel.collidepoint(mx, my):
            self.layout_swap_mode = False
            self.layout_swap_first_room = None
            return

        # Raum auf dem Spielerschiff anklicken
        for room in self.data.player.ship.rooms:
            if room.rect.collidepoint(int(mx), int(my)):
                if self.layout_swap_first_room is None:
                    self.layout_swap_first_room = room
                    self.data.combat.msg = f"1. RAUM ({room.name.upper()}) GEWÄHLT! KLICKE AUF DEN 2. RAUM."
                    self.data.combat.msg_timer = 3.0
                elif room != self.layout_swap_first_room:
                    r1 = self.layout_swap_first_room
                    r2 = room
                    self.data.player.scrap -= 15
                    self.data.player.ship.swap_room_systems(r1, r2)
                    self.data.combat.msg = f"LAYOUT-UMBAU: {r1.name.upper()} UND {r2.name.upper()} GETAUSCHT!"
                    self.data.combat.msg_timer = 3.0
                    self.layout_swap_mode = False
                    self.layout_swap_first_room = None
                return
                self.sell_weapon_at_slot(idx)
                return

    def handle_slot_selection_click(self, mx: float, my: float):
        item = self.selecting_slot_item
        if not item:
            return

        # Abbrechen Button
        btn_cancel = pygame.Rect(320, 420, 240, 38)
        if btn_cancel.collidepoint(mx, my):
            self.selecting_slot_item = None
            return

        # Slot-Buttons
        max_slots = getattr(self.data.player.ship, "max_weapons", 3)
        for slot_idx in range(max_slots):
            slot_btn = pygame.Rect(150, 150 + slot_idx * 65, 600, 52)
            if slot_btn.collidepoint(mx, my):
                self.buy_weapon_to_slot(item, slot_idx)
                return

    def buy_weapon_to_slot(self, item: dict, slot_idx: int):
        price = item.get("price", 40)
        if self.data.player.scrap < price:
            self.data.combat.msg = "NICHT GENUG SCRAP!"
            self.data.combat.msg_timer = 1.8
            return

        slots = getattr(self.data.player.ship, "weapon_slots", [])
        if slot_idx < len(slots):
            allowed = slots[slot_idx].get("allowed_types")
            if allowed and item["w_type"] not in allowed:
                self.data.combat.msg = f"SLOT {slot_idx+1} ERLAUBT NUR: {', '.join(allowed)}!"
                self.data.combat.msg_timer = 2.5
                return

        # Ist der Slot aktuell belegt?
        if slot_idx < len(self.data.player.weapons):
            cur_w = self.data.player.weapons[slot_idx]
            # Ist es der gleiche Waffentyp -> WAFFEN-FUSION!
            if cur_w.w_type == item["w_type"]:
                if cur_w.level < 5:
                    self.data.player.scrap -= price
                    cur_w.upgrade()
                    if hasattr(self.data, "achievements"):
                        self.data.achievements.unlock("weapon_fuser")
                    self.data.combat.msg = f"FUSION AN SLOT {slot_idx+1}! {cur_w.name} ist nun Stufe {cur_w.level} (MK {cur_w.level})!"
                    self.data.combat.msg_timer = 2.8
                    self.selecting_slot_item = None
                else:
                    self.data.combat.msg = f"MAXIMALES FUSION-LEVEL (MK V) AN SLOT {slot_idx+1} ERREICHT!"
                    self.data.combat.msg_timer = 2.2
                return
            else:
                # Waffe ersetzen & alte Waffe zum halben Wert verkaufen
                refund = max(10, 15 * cur_w.level)
                self.data.player.scrap -= price
                self.data.player.scrap += refund
                self.data.player.weapons[slot_idx] = Weapon(
                    item["name"],
                    charge_time=item["charge_time"],
                    w_type=item["w_type"],
                    shield_pierce=item["shield_pierce"],
                    damage=item["damage"],
                    ammo_cost=item["ammo_cost"],
                    subtype=item.get("subtype", "STANDARD"),
                    fire_chance=item.get("fire_chance", 0.0),
                    breach_chance=item.get("breach_chance", 0.0),
                    stun_duration=item.get("stun_duration", 0.0),
                    crew_damage=item.get("crew_damage", 0.0),
                )
                self.data.combat.msg = f"ERSETZT AN SLOT {slot_idx+1}: {item['name']} eingebaut (+{refund} Scrap Altverkauf)!"
                self.data.combat.msg_timer = 2.8
                self.selecting_slot_item = None
                return
        else:
            # Slot ist frei -> Einbauen
            self.data.player.scrap -= price
            new_w = Weapon(
                item["name"],
                charge_time=item["charge_time"],
                w_type=item["w_type"],
                shield_pierce=item["shield_pierce"],
                damage=item["damage"],
                ammo_cost=item["ammo_cost"],
                subtype=item.get("subtype", "STANDARD"),
                fire_chance=item.get("fire_chance", 0.0),
                breach_chance=item.get("breach_chance", 0.0),
                stun_duration=item.get("stun_duration", 0.0),
                crew_damage=item.get("crew_damage", 0.0),
            )
            self.data.player.weapons.append(new_w)
            self.data.combat.msg = f"GEKAUFT: {item['name']} an Slot {slot_idx+1} eingebaut!"
            self.data.combat.msg_timer = 2.5
            self.selecting_slot_item = None

    def sell_weapon_at_slot(self, slot_idx: int):
        if 0 <= slot_idx < len(self.data.player.weapons):
            w = self.data.player.weapons[slot_idx]
            refund = max(15, 15 * w.level)
            self.data.player.scrap += refund
            self.data.player.weapons.pop(slot_idx)
            self.data.combat.msg = f"{w.name} für {refund} Scrap verkauft!"
            self.data.combat.msg_timer = 2.0

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
                name=f"Rekrut #{c_num}",
                species=species,
            )
        )
        if len(self.data.player.crew) >= 6 and hasattr(self.data, "achievements"):
            self.data.achievements.unlock("full_house")

    def buy_augment(self, item: dict):
        name = item["name"]
        price = item.get("price", 60)
        augments = getattr(self.data.player, "augments", [])
        if name in augments:
            self.data.combat.msg = f"{name.upper()} BEREITS AUSGERÜSTET!"
            self.data.combat.msg_timer = 2.0
            return
        if len(augments) >= 3:
            self.data.combat.msg = "MAXIMAL 3 AUGMENTATIONS ERLAUBT!"
            self.data.combat.msg_timer = 2.0
            return
        if self.data.player.scrap < price:
            self.data.combat.msg = "NICHT GENUG SCRAP!"
            self.data.combat.msg_timer = 1.8
            return

        self.data.player.scrap -= price
        augments.append(name)
        self.data.player.augments = augments
        self.data.combat.msg = f"{name.upper()} GEKAUFT & AUSGERÜSTET!"
        self.data.combat.msg_timer = 2.5

    def leave_shop(self):
        self.selecting_slot_item = None
        self.data.current_state = STATE_MAP