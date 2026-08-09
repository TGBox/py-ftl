from typing import TYPE_CHECKING

    
import random
from typing import Any
import pygame

from classes.Crew import Crew
from classes.GameData import GameData
from classes.Room import Room
from classes.Weapon import Weapon
from settings import *

if TYPE_CHECKING:
    from game import Game

WEAPON_CATALOG_MASTER: list[dict[str, Any]] = [
    {"name": "Standard Laser", "charge_time": 3.0, "w_type": "LASER", "shield_pierce": 0, "damage": 25.0, "ammo_cost": 0, "price": 30, "subtype": "STANDARD", "max_range": 650.0},
    {"name": "Schwerer Laser", "charge_time": 3.5, "w_type": "LASER", "shield_pierce": 0, "damage": 45.0, "ammo_cost": 0, "price": 50, "subtype": "HEAVY", "max_range": 600.0},
    {"name": "Burst Laser MK II", "charge_time": 4.0, "w_type": "LASER", "shield_pierce": 0, "damage": 60.0, "ammo_cost": 0, "price": 70, "subtype": "STANDARD", "max_range": 600.0},
    {"name": "Artemis Rakete", "charge_time": 4.0, "w_type": "MISSILE", "shield_pierce": 1, "damage": 40.0, "ammo_cost": 1, "price": 40, "subtype": "STANDARD", "crew_damage": 35.0},
    {"name": "Hermes Rakete", "charge_time": 4.5, "w_type": "MISSILE", "shield_pierce": 1, "damage": 50.0, "ammo_cost": 1, "price": 65, "subtype": "HEAVY", "crew_damage": 45.0},
    {"name": "Pike Strahl", "charge_time": 5.0, "w_type": "BEAM", "shield_pierce": 1, "damage": 35.0, "ammo_cost": 0, "price": 60, "subtype": "STANDARD", "max_range": 500.0},
    {"name": "Halberd Strahl", "charge_time": 5.5, "w_type": "BEAM", "shield_pierce": 1, "damage": 45.0, "ammo_cost": 0, "price": 75, "subtype": "STANDARD", "max_range": 550.0},
    {"name": "Ion Blast MK I", "charge_time": 3.0, "w_type": "ION", "shield_pierce": 0, "damage": 10.0, "ammo_cost": 0, "price": 45, "subtype": "STANDARD"},
    {"name": "Bio-Strahl MK I", "charge_time": 4.5, "w_type": "BEAM", "shield_pierce": 0, "damage": 0.0, "ammo_cost": 0, "price": 65, "subtype": "BIO", "crew_damage": 65.0, "max_range": 480.0},
    {"name": "Brand-Laser MK I", "charge_time": 3.8, "w_type": "LASER", "shield_pierce": 0, "damage": 15.0, "ammo_cost": 0, "price": 55, "subtype": "FIRE", "fire_chance": 0.75, "max_range": 600.0},
    {"name": "Betäubungs-Ion MK I", "charge_time": 3.0, "w_type": "ION", "shield_pierce": 0, "damage": 10.0, "ammo_cost": 0, "price": 50, "subtype": "STUN", "stun_duration": 6.0, "max_range": 550.0},
    {"name": "Schwerer Hüllenbrecher", "charge_time": 4.2, "w_type": "LASER", "shield_pierce": 0, "damage": 35.0, "ammo_cost": 0, "price": 60, "subtype": "BREACH", "breach_chance": 0.60, "max_range": 580.0},
    {"name": "Anti-Materie Kanone", "charge_time": 4.8, "w_type": "MISSILE", "shield_pierce": 1, "damage": 10.0, "ammo_cost": 1, "price": 75, "subtype": "BIO", "crew_damage": 85.0},
    {"name": "Feuer-Bombe", "charge_time": 4.5, "w_type": "BOMB", "shield_pierce": 99, "damage": 0.0, "ammo_cost": 1, "price": 55, "subtype": "FIRE", "fire_chance": 0.90, "max_range": 420.0},
    {"name": "Hüllenbruch-Bombe", "charge_time": 5.0, "w_type": "BOMB", "shield_pierce": 99, "damage": 15.0, "ammo_cost": 1, "price": 60, "subtype": "BREACH", "breach_chance": 0.90, "max_range": 420.0},
    {"name": "Kurzstrecken-Flak", "charge_time": 3.2, "w_type": "FLAK", "shield_pierce": 0, "damage": 30.0, "ammo_cost": 0, "price": 45, "subtype": "STANDARD", "max_range": 350.0},
    {"name": "Impuls-Laser (Kurz)", "charge_time": 2.5, "w_type": "LASER", "shield_pierce": 0, "damage": 25.0, "ammo_cost": 0, "price": 40, "subtype": "STANDARD", "max_range": 320.0},
]


AUGMENT_CATALOG_MASTER: list[dict[str, Any]] = [
    {"name": "Waffen-Vorheizer", "type": "AUGMENT", "desc": "Waffen starten zu 100% geladen!", "price": 80},
    {"name": "Schild-Booster", "type": "AUGMENT", "desc": "+30% Schild-Erholung!", "price": 60},
    {"name": "Automatisierte Relais", "type": "AUGMENT", "desc": "Repariert Räume automatisch!", "price": 50},
    {"name": "Sauerstoff-Konverter", "type": "AUGMENT", "desc": "+50% O2-Regeneration!", "price": 40},
    {"name": "Schrott-Arm", "type": "AUGMENT", "desc": "+30% Schrott-Beute!", "price": 55},
]


SYSTEM_ROOM_CATALOG: list[dict[str, Any]] = [
    {"name": "Medbay", "desc": "Heilt Crew-Mitglieder im Raum", "price": 50, "max_power": 3},
    {"name": "Teleporter", "desc": "Entern feindlicher Schiffe", "price": 60, "max_power": 2},
    {"name": "Tarnung", "desc": "Unsichtbarkeit & Ausweichen im Kampf", "price": 80, "max_power": 3},
    {"name": "Drohnen-Kontrolle", "desc": "Steuerung von Kampf- & Rep-Drohnen", "price": 75, "max_power": 3},
    {"name": "Sensoren", "desc": "Sicht auf feindliche Schiffsräume & Crew", "price": 40, "max_power": 2},
]

PROTECTED_CORE_SYSTEMS = ["Brücke", "Schild", "Waffen", "Antrieb", "Reaktor"]


class ShopManager:

    def __init__(self, data: GameData):
        self.data = data
        self.game: Game | None = None   # Set by Game after construction
        self.catalog_stock: list[dict[str, Any]] = []
        self.selecting_slot_item: dict[str, Any] | None = None
        self.layout_swap_mode: bool = False
        self.layout_swap_type: str = "ROOMS"  # "ROOMS" oder "WEAPONS"
        self.layout_swap_first_selection = None
        self.active_tab: str = "RESOURCES"  # "RESOURCES", "WEAPONS", "CREW", "ROOMS"
        self.next_crew_candidate: dict[str, Any] | None = None

        # Tab-Buttons oben (überlappungsfrei unter dem Ressourcen-Header)
        self.tab_resources = pygame.Rect(75, 96, 170, 28)
        self.tab_weapons = pygame.Rect(255, 96, 170, 28)
        self.tab_crew = pygame.Rect(435, 96, 170, 28)
        self.tab_rooms = pygame.Rect(615, 96, 170, 28)

        # Tab 1: Ressourcen-Buttons
        self.btn_repair = pygame.Rect(100, 130, 340, 36)
        self.btn_fuel = pygame.Rect(100, 180, 340, 36)
        self.btn_missiles = pygame.Rect(100, 230, 340, 36)
        self.btn_drone_parts = pygame.Rect(100, 280, 340, 36)
        self.btn_upgrade_reactor = pygame.Rect(100, 330, 340, 36)

        # Tab 2: Waffen & Layout
        self.btn_edit_layout = pygame.Rect(100, 130, 340, 36)

        # Tab 3: Crew
        self.btn_buy_crew = pygame.Rect(100, 350, 340, 44)

        # Gemeinsamer Beenden-Button
        self.btn_leave_shop = pygame.Rect(340, 495, 220, 40)

        self.refresh_catalog()
        self.generate_next_crew_candidate()

    def generate_next_crew_candidate(self):
        species_perks = {
            "Mensch": "Ausgewogener Allrounder (Standard-Reparatur & Kampf)",
            "Engi": "+100% Reparaturspeed, verringerter Kampfschaden",
            "Mantis": "+50% Nahkampfschaden, verringertes Reparieren",
            "Rock": "+50 Max HP & volle Immunität gegen Feuer",
            "Zoltan": "Spendet +1 Gratis-Energie für den aktuellen Raum",
        }
        species = random.choice(["Mensch", "Engi", "Mantis", "Rock", "Zoltan"])
        c_num = len(self.data.player.crew) + 1
        self.next_crew_candidate = {
            "name": f"Rekrut #{c_num}",
            "species": species,
            "price": 25,
            "perks": species_perks.get(species, "Spezialist"),
        }

    def is_weapon_compatible(self, weapon: dict[str, Weapon]) -> bool:
        """Prüft, ob eine Waffe in mindestens einen Waffenslot des aktuellen Spielerschiffs passt."""
        ship = getattr(self.data.player, "ship", None)
        if not ship:
            return True
        slots = getattr(ship, "weapon_slots", [])
        if not slots:
            return True
        w_type = weapon.get("w_type")
        for slot in slots:
            allowed = slot.get("allowed_types")
            if not allowed or w_type in allowed:
                return True
        return False

    def refresh_catalog(self):
        compatible = [w for w in WEAPON_CATALOG_MASTER if self.is_weapon_compatible(w)]
        incompatible = [w for w in WEAPON_CATALOG_MASTER if not self.is_weapon_compatible(w)]

        w_sample: list[dict[str, Any]] = []
        avail_comp = list(compatible)
        avail_incomp = list(incompatible)
        avail_all = list(WEAPON_CATALOG_MASTER)

        target_weapon_count = min(2, len(WEAPON_CATALOG_MASTER))

        for _ in range(target_weapon_count):
            use_compatible = (random.random() < 0.90) and len(avail_comp) > 0
            if use_compatible:
                w = random.choice(avail_comp)
            else:
                pool = avail_incomp if len(avail_incomp) > 0 else avail_all
                if not pool:
                    break
                w = random.choice(pool)

            w_sample.append(w)
            if w in avail_comp:
                avail_comp.remove(w)
            if w in avail_incomp:
                avail_incomp.remove(w)
            if w in avail_all:
                avail_all.remove(w)

        a_sample = random.sample(AUGMENT_CATALOG_MASTER, min(1, len(AUGMENT_CATALOG_MASTER)))
        self.catalog_stock: list[dict[str, Any]] = list(w_sample + a_sample)
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

        # 1. Tab-Wechsel-Klicks
        if self.tab_resources.collidepoint(mx, my):
            self.active_tab = "RESOURCES"
            return
        elif self.tab_weapons.collidepoint(mx, my):
            self.active_tab = "WEAPONS"
            return
        elif self.tab_crew.collidepoint(mx, my):
            self.active_tab = "CREW"
            return
        elif self.tab_rooms.collidepoint(mx, my):
            self.active_tab = "ROOMS"
            return

        # 2. Beenden Button
        if self.btn_leave_shop.collidepoint(mx, my):
            self.leave_shop()
            return

        # 3. Tab-Spezifische Klicks
        if self.active_tab == "RESOURCES":
            if self.btn_repair.collidepoint(mx, my):
                self.buy_repair()
            elif self.btn_fuel.collidepoint(mx, my):
                self.buy_fuel()
            elif self.btn_missiles.collidepoint(mx, my):
                self.buy_missiles()
            elif self.btn_drone_parts.collidepoint(mx, my):
                self.buy_drone_parts()
            elif self.btn_upgrade_reactor.collidepoint(mx, my):
                self.upgrade_reactor()

        elif self.active_tab == "WEAPONS":
            if self.btn_edit_layout.collidepoint(mx, my):
                self.start_layout_swap()
                return

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
            for idx in range(min(len(self.data.player.weapons), max_slots)):
                w = self.data.player.weapons[idx]
                if w is None:
                    continue
                card_x = 80 + idx * (card_w + 12)
                sell_btn = pygame.Rect(card_x + 6, 412, card_w - 12, 22)
                if sell_btn.collidepoint(mx, my):
                    self.sell_weapon_at_slot(idx)
                    return

        elif self.active_tab == "CREW":
            if self.btn_buy_crew.collidepoint(mx, my):
                self.buy_crew()

        elif self.active_tab == "ROOMS":
            # Kauf eines neuen Systems für leeren Raum-Slot
            for idx, sys_item in enumerate(SYSTEM_ROOM_CATALOG):
                buy_btn = pygame.Rect(100, 140 + idx * 55, 340, 42)
                if buy_btn.collidepoint(mx, my):
                    self.buy_room_system(sys_item)
                    return

            # Verkauf von Zusatzsystemen auf dem Schiff
            empty_or_optional_rooms = [
                r for r in self.data.player.ship.rooms
                if r.name not in PROTECTED_CORE_SYSTEMS and r.name != "[Freier Raum-Slot]"
            ]
            for idx, r in enumerate(empty_or_optional_rooms):
                sell_btn = pygame.Rect(470, 140 + idx * 55, 350, 42)
                if sell_btn.collidepoint(mx, my):
                    self.sell_room_system(r)
                    return

    def start_layout_swap(self):
        if self.data.player.scrap < 15:
            self.data.combat.msg = "NICHT GENUG SCRAP FÜR LAYOUT-UMBAU (15 SCRAP BENÖTIGT)!"
            self.data.combat.msg_timer = 2.0
            return
        self.layout_swap_mode = True
        self.layout_swap_type = "ROOMS"
        self.layout_swap_first_selection = None
        self.data.combat.msg = "LAYOUT-UMBAU: WÄHLE RÄUME ODER WAFFENSLOTS ZUM TAUSCHEN!"
        self.data.combat.msg_timer = 3.0

    def handle_layout_swap_click(self, mx: float, my: float):
        btn_cancel = pygame.Rect(320, 490, 260, 40)
        if btn_cancel.collidepoint(mx, my):
            self.layout_swap_mode = False
            self.layout_swap_first_selection = None
            return

        # Tab-Buttons für Tauschmodus (Räume vs. Waffenslots)
        tab_rooms = pygame.Rect(200, 50, 190, 32)
        tab_weapons = pygame.Rect(410, 50, 190, 32)
        if tab_rooms.collidepoint(mx, my):
            self.layout_swap_type = "ROOMS"
            self.layout_swap_first_selection = None
            self.data.combat.msg = "RAUM-TAUSCH MODUS GEWÄHLT."
            self.data.combat.msg_timer = 2.0
            return
        if tab_weapons.collidepoint(mx, my):
            self.layout_swap_type = "WEAPONS"
            self.layout_swap_first_selection = None
            self.data.combat.msg = "WAFFENSLOT-TAUSCH MODUS GEWÄHLT."
            self.data.combat.msg_timer = 2.0
            return

        if getattr(self, "layout_swap_type", "ROOMS") == "ROOMS":
            for room in self.data.player.ship.rooms:
                if room.rect.collidepoint(int(mx), int(my)):
                    if self.layout_swap_first_selection is None:
                        self.layout_swap_first_selection = room
                        self.data.combat.msg = f"1. RAUM ({room.name.upper()}) GEWÄHLT! KLICKE AUF DEN 2. RAUM."
                        self.data.combat.msg_timer = 3.0
                    elif room != self.layout_swap_first_selection and hasattr(self.layout_swap_first_selection, "name"):
                        if isinstance(self.layout_swap_first_selection, Room):
                            r1: Room = self.layout_swap_first_selection
                            self.data.player.ship.swap_room_systems(r1, room)
                            self.data.player.scrap -= 15
                            self.data.combat.msg = f"LAYOUT-UMBAU: {r1.name.upper()} UND {room.name.upper()} GETAUSCHT!"
                            self.data.combat.msg_timer = 3.0
                            self.layout_swap_mode = False
                            self.layout_swap_first_selection = None
                    return
        else:
            for idx, slot in enumerate(self.data.player.ship.weapon_slots):
                pos: tuple[int, int] = slot.get("pos", (0, 0))
                hx, hy = pos
                slot_rect = pygame.Rect(hx - 65, hy - 25, 130, 50)
                if slot_rect.collidepoint(int(mx), int(my)):
                    if self.layout_swap_first_selection is None:
                        self.layout_swap_first_selection = idx
                        self.data.combat.msg = f"1. WAFFENSLOT H{idx+1} GEWÄHLT! KLICKE AUF DEN 2. SLOT."
                        self.data.combat.msg_timer = 3.0
                    elif idx != self.layout_swap_first_selection and isinstance(self.layout_swap_first_selection, int):
                        s1 = self.layout_swap_first_selection
                        s2 = idx
                        self.data.player.scrap -= 15
                        assert self.data.player.weapons is not None
                        self.data.player.ship.swap_weapon_slots(s1, s2, self.data.player.weapons)
                        self.data.combat.msg = f"LAYOUT-UMBAU: WAFFENSLOT H{s1+1} UND H{s2+1} GETAUSCHT!"
                        self.data.combat.msg_timer = 3.0
                        self.layout_swap_mode = False
                        self.layout_swap_first_selection = None
                    return

    def handle_slot_selection_click(self, mx: float, my: float):
        item = self.selecting_slot_item
        if not item:
            return

        btn_cancel = pygame.Rect(320, 420, 240, 38)
        if btn_cancel.collidepoint(mx, my):
            self.selecting_slot_item = None
            return

        max_slots = getattr(self.data.player.ship, "max_weapons", 3)
        for slot_idx in range(max_slots):
            slot_btn = pygame.Rect(150, 150 + slot_idx * 65, 600, 52)
            if slot_btn.collidepoint(mx, my):
                self.buy_weapon_to_slot(item, slot_idx)
                return
    
    def buy_weapon_to_slot(self, item: dict[str, Any], slot_idx: int) -> None:
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

        # Ist der Slot belegt?
        if slot_idx < len(self.data.player.weapons) and self.data.player.weapons[slot_idx] is not None:
            cur_w = self.data.player.weapons[slot_idx]
            if cur_w is not None:
                if cur_w.w_type == item["w_type"]:
                    if cur_w.level < 5:
                        self.data.player.scrap -= price
                        cur_w.upgrade()
                        if hasattr(self.data, "achievements"):
                            assert self.game is not None
                            self.game.achievement_manager.unlock("weapon_fuser")
                        self.data.combat.msg = f"FUSION AN SLOT {slot_idx+1}! {cur_w.name} ist nun Stufe {cur_w.level} (MK {cur_w.level})!"
                        self.data.combat.msg_timer = 2.8
                        self.selecting_slot_item = None
                    else:
                        self.data.combat.msg = f"MAXIMALES FUSION-LEVEL (MK V) AN SLOT {slot_idx+1} ERREICHT!"
                        self.data.combat.msg_timer = 2.2
                    return
            else:
                # TODO 48: Verhindere versehentliches Überschreiben ohne expliziten Verkauf!
                if cur_w is not None:
                    self.data.combat.msg = f"SLOT {slot_idx+1} BELEGT! Verkaufe zuerst die alte Waffe ({cur_w.name})!"
                    self.data.combat.msg_timer = 3.0
                return
        else:
            # Slot frei -> Einbauen
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
                max_range=item.get("max_range"),
            )
            while len(self.data.player.weapons) <= slot_idx:
                self.data.player.weapons.append(None)
            self.data.player.weapons[slot_idx] = new_w

            self.data.combat.msg = f"GEKAUFT: {item['name']} an Slot {slot_idx+1} eingebaut!"
            self.data.combat.msg_timer = 2.5
            self.selecting_slot_item = None

    def sell_weapon_at_slot(self, slot_idx: int):
        if 0 <= slot_idx < len(self.data.player.weapons):
            w = self.data.player.weapons[slot_idx]
            if w is not None:
                refund = max(15, 15 * w.level)
                self.data.player.scrap += refund
                # TODO 42: Platzhalter setzen um Nachrücken zu verhindern
                self.data.player.weapons[slot_idx] = None
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

    def buy_drone_parts(self):
        if self.data.player.scrap < 6:
            self.data.combat.msg = "NICHT GENUG SCRAP FÜR DROHNENTEILE!"
            self.data.combat.msg_timer = 1.8
            return
        self.data.player.scrap -= 6
        self.data.player.drone_parts += 2
        self.data.combat.msg = "2 DROHNENTEILE GEKAUFT! (+2 Drohnenteile)"
        self.data.combat.msg_timer = 2.0

    def upgrade_reactor(self):
        # TODO 39: Reaktorleistungs-Begrenzung auf maximale Raumpower
        max_needed = sum(r.max_power for r in self.data.player.ship.rooms)
        if self.data.player.reactor.total_power >= max_needed:
            self.data.combat.msg = f"MAXIMALE REAKTORLEISTUNG ({max_needed} ENERGIE) FÜR DIESES SCHIFF ERREICHT!"
            self.data.combat.msg_timer = 2.5
            return
        if self.data.player.scrap < 15:
            self.data.combat.msg = "NICHT GENUG SCRAP FÜR REAKTOR-UPGRADE (15 SCRAP BENÖTIGT)!"
            self.data.combat.msg_timer = 2.0
            return
        self.data.player.scrap -= 15
        self.data.player.reactor.total_power += 1
        self.data.player.reactor.available_power += 1
        self.data.combat.msg = f"REAKTOR AUFGERÜSTET! ({self.data.player.reactor.total_power} Power)"
        self.data.combat.msg_timer = 2.0

    def buy_crew(self):
        max_c = getattr(self.data.player.ship, "max_crew", 4)
        cand = self.next_crew_candidate or {}
        price = cand.get("price", 25)
        if self.data.player.scrap < price:
            self.data.combat.msg = "NICHT GENUG SCRAP!"
            self.data.combat.msg_timer = 1.8
            return
        if len(self.data.player.crew) >= max_c:
            self.data.combat.msg = f"MAXIMALE CREW-GRÖSSE ({max_c}) ERREICHT!"
            self.data.combat.msg_timer = 2.0
            return
        self.data.player.scrap -= price
        spawn_room = self.data.player.ship.rooms[0]
        species = cand.get("species", "Mensch")
        name = cand.get("name", "Rekrut")
        self.data.player.crew.append(
            Crew(
                spawn_room.rect.centerx,
                spawn_room.rect.centery,
                name=name,
                species=species,
            )
        )
        self.data.combat.msg = f"{name} ({species}) ANGEHEUERT!"
        self.data.combat.msg_timer = 2.5
        self.generate_next_crew_candidate()
        if len(self.data.player.crew) >= 6 and hasattr(self.data, "achievements"):
            assert self.game is not None
            self.game.achievement_manager.unlock("full_house")

    def buy_room_system(self, sys_item: dict[str, Any]):
        price = sys_item.get("price", 50)
        if self.data.player.scrap < price:
            self.data.combat.msg = "NICHT GENUG SCRAP!"
            self.data.combat.msg_timer = 1.8
            return

        sys_name = sys_item["name"]
        # Ist das System bereits auf dem Schiff vorhanden?
        existing = [r for r in self.data.player.ship.rooms if r.name == sys_name]
        if existing:
            self.data.combat.msg = f"SYSTEM {sys_name.upper()} IST BEREITS INSTALLIERT!"
            self.data.combat.msg_timer = 2.2
            return

        # Suche nach freiem Raum-Slot
        free_room = next((r for r in self.data.player.ship.rooms if r.name == "[Freier Raum-Slot]"), None)
        if not free_room:
            self.data.combat.msg = "KEIN FREIER RAUM-SLOT VERFÜGBAR! Verkaufe zuerst ein Zusatzsystem."
            self.data.combat.msg_timer = 2.8
            return

        self.data.player.scrap -= price
        free_room.name = sys_name
        free_room.max_power = sys_item.get("max_power", 3)
        free_room.current_power = 0
        free_room.health = free_room.max_health
        self.data.combat.msg = f"SYSTEM {sys_name.upper()} ERFOLGREICH INSTALLIERT!"
        self.data.combat.msg_timer = 2.5

    def sell_room_system(self, room: Room):
        if room.name in PROTECTED_CORE_SYSTEMS:
            self.data.combat.msg = f"KERNSYSTEM {room.name.upper()} KANN NICHT VERKAUFT WERDEN!"
            self.data.combat.msg_timer = 2.2
            return

        # Finde Preis aus System-Katalog
        cat_info = next((item for item in SYSTEM_ROOM_CATALOG if item["name"] == room.name), None)
        base_price = cat_info["price"] if cat_info else 40
        refund = base_price // 2

        # Strom aus dem Raum abziehen und Reaktor zurückgeben
        if room.current_power > 0:
            self.data.player.reactor.available_power += room.current_power
            room.current_power = 0

        sold_name = room.name
        room.name = "[Freier Raum-Slot]"
        room.max_power = 0
        self.data.player.scrap += refund
        self.data.combat.msg = f"SYSTEM {sold_name.upper()} VERKAUFT (+{refund} Scrap)!"
        self.data.combat.msg_timer = 2.5

    def buy_augment(self, item: dict[str, str]):
        name = item["name"]
        price = int(item.get("price", 60))
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