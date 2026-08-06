import random

from classes.Crew import Crew
from classes.GameData import GameData
from classes.Projectile import Projectile
from managers.state_manager import StateManager
from settings import *


class CombatManager:

    def __init__(self, data: GameData, state_manager: StateManager):
        self.data = data
        self.state_manager = state_manager
        self.enemy_crew: list[Crew] = []
        self.sound = None  # Set by Game after construction

    def update(self, dt: float):
        """Wird einmal pro Frame aufgerufen."""

        if self.data.paused or getattr(self.data, "show_pause_menu", False):
            return

        if self.data.current_state not in (STATE_MAIN_MENU, STATE_GAME_OVER, STATE_VICTORY):
            self.data.player.ship.update_doors(dt)
            self.data.enemy.ship.update_doors(dt)
            self.update_crew(dt)

            if len(self.data.player.crew) == 0:
                if self.sound: self.sound.play("game_over")
                self.player_lost()
                return

        if self.data.current_state != STATE_COMBAT:
            self.was_in_combat = False
            return

        if not getattr(self, "was_in_combat", False):
            self.was_in_combat = True
            if "Waffen-Vorheizer" in getattr(self.data.player, "augments", []):
                for w in self.data.player.weapons:
                    w.current_charge = w.charge_time
                self.show_message("WAFFEN-VORHEIZER AKTIV! Waffen voll geladen!")

        self.data.combat.msg_timer = max(
            0.0,
            self.data.combat.msg_timer - dt
        )
        self.data.combat.cloak_active_timer = max(
            0.0,
            getattr(self.data.combat, "cloak_active_timer", 0.0) - dt
        )
        self.data.combat.cloak_cooldown = max(
            0.0,
            getattr(self.data.combat, "cloak_cooldown", 0.0) - dt
        )

        # Umweltgefahren Verarbeitung (Solar Flares & Asteroid Fields)
        current_node = self.data.world.star_map.current_node
        hazard = getattr(current_node, "hazard_type", "NONE") if current_node else "NONE"

        if hazard == "SOLAR_FLARE":
            self.data.combat.solar_flare_flash = max(0.0, getattr(self.data.combat, "solar_flare_flash", 0.0) - dt)
            sf_timer = getattr(self.data.combat, "solar_flare_timer", 20.0) - dt
            if sf_timer <= 0.0:
                self.data.combat.solar_flare_timer = 22.0
                self.data.combat.solar_flare_flash = 0.6
                p_targets = random.sample(self.data.player.ship.rooms, min(2, len(self.data.player.ship.rooms)))
                e_targets = random.sample(self.data.enemy.ship.rooms, min(2, len(self.data.enemy.ship.rooms)))
                for r in p_targets + e_targets:
                    r.fire_level = min(100.0, r.fire_level + 45.0)
                if self.sound: self.sound.play("explosion")
                self.show_message("SONNEN-ERUPTION! BRÄNDE AUF BEIDEN SCHIFFEN ENTFACHT!")
            else:
                self.data.combat.solar_flare_timer = sf_timer

        elif hazard == "ASTEROID_FIELD":
            ast_timer = getattr(self.data.combat, "asteroid_timer", 2.5) - dt
            if ast_timer <= 0.0:
                self.data.combat.asteroid_timer = random.uniform(2.0, 3.5)
                # Asteroid schlägt in zufälligen Raum ein
                if random.random() < 0.5 and self.data.player.ship.rooms:
                    t_room = random.choice(self.data.player.ship.rooms)
                    self.data.player.projectiles.append(
                        Projectile((0, random.randint(100, 400)), t_room.rect.center, target_room=t_room, is_player_shot=False, w_type="LASER", damage=20.0)
                    )
                elif self.data.enemy.ship.rooms:
                    t_room = random.choice(self.data.enemy.ship.rooms)
                    self.data.player.projectiles.append(
                        Projectile((0, random.randint(100, 400)), t_room.rect.center, target_room=t_room, is_player_shot=True, w_type="LASER", damage=20.0)
                    )
            else:
                self.data.combat.asteroid_timer = ast_timer

        # ------------------------------------------------------
        # DROHNEN-SIMULATION (Combat Drones & Repair Drones)
        # ------------------------------------------------------
        drone_room = next((r for r in self.data.player.ship.rooms if r.name == "Drohnen-Kontrolle"), None)
        drone_power = drone_room.current_power if (drone_room and drone_room.health > 10) else 0

        # 1. Kampfdrohne (Orbit & Laserfeuer auf Gegnerschiff)
        if getattr(self.data.combat, "combat_drone_active", False):
            if drone_power < 1:
                self.data.combat.combat_drone_active = False
                self.show_message("KAMPFDROHNE DEAKTIVIERT (Keine Drohnen-Energie)!")
            else:
                import math
                self.data.combat.drone_orbit_angle = (getattr(self.data.combat, "drone_orbit_angle", 0.0) + 1.2 * dt) % (2 * math.pi)
                self.data.combat.drone_fire_timer = getattr(self.data.combat, "drone_fire_timer", 0.0) - dt
                if self.data.combat.drone_fire_timer <= 0.0:
                    self.data.combat.drone_fire_timer = 4.5
                    if self.data.enemy.ship.rooms:
                        t_room = random.choice(self.data.enemy.ship.rooms)
                        ang = self.data.combat.drone_orbit_angle
                        d_x = int(670 + math.cos(ang) * 160)
                        d_y = int(240 + math.sin(ang) * 110)
                        self.data.player.projectiles.append(
                            Projectile((d_x, d_y), t_room.rect.center, target_room=t_room, is_player_shot=True, w_type="LASER", damage=25.0)
                        )
                        if self.sound: self.sound.play("laser_fire")

        # 2. Reparaturdrohne (Autonome Reparatur & Brandbekämpfung)
        if getattr(self.data.combat, "repair_drone_active", False):
            if drone_power < 2:
                self.data.combat.repair_drone_active = False
                self.show_message("REPARATURDROHNE DEAKTIVIERT (Braucht 2 Drohnen-Energie)!")
            else:
                import math
                rx, ry = getattr(self.data.combat, "repair_drone_pos", (160.0, 245.0))
                damaged_rooms = [r for r in self.data.player.ship.rooms if r.health < r.max_health or r.fire_level > 0 or r.has_breach]
                target_room = damaged_rooms[0] if damaged_rooms else self.data.player.ship.rooms[0]

                tx, ty = float(target_room.rect.centerx), float(target_room.rect.centery)
                dx, dy = tx - rx, ty - ry
                dist = math.hypot(dx, dy)
                if dist < 140.0 * dt:
                    rx, ry = tx, ty
                    if damaged_rooms:
                        target_room.repair(30.0 * dt)
                else:
                    rx += (dx / dist) * 140.0 * dt
                    ry += (dy / dist) * 140.0 * dt
                self.data.combat.repair_drone_pos = (rx, ry)

        # ------------------------------------------------------
        # FLAGGSCHIFF BOSS MECHANIKEN (Phase 2 Surge & Phase 3 Boarders)
        # ------------------------------------------------------
        if "Flaggschiff" in getattr(self.data.enemy.ship, "name", ""):
            b_phase = getattr(self.data.combat, "boss_phase", 1)
            if b_phase == 2:
                self.data.combat.drone_surge_timer = getattr(self.data.combat, "drone_surge_timer", 18.0) - dt
                if self.data.combat.drone_surge_timer <= 0.0:
                    self.data.combat.drone_surge_timer = 18.0
                    self.show_message("ACHTUNG! DROHNENSCHWARM POWER SURGE!")
                    if self.sound: self.sound.play("alarm")
                    for _ in range(4):
                        if self.data.player.ship.rooms:
                            t_r = random.choice(self.data.player.ship.rooms)
                            self.data.player.projectiles.append(
                                Projectile((700, random.randint(100, 400)), t_r.rect.center, target_room=t_r, is_player_shot=False, w_type="LASER", damage=25.0)
                            )
            elif b_phase == 3:
                self.data.combat.boss_teleport_timer = getattr(self.data.combat, "boss_teleport_timer", 20.0) - dt
                if self.data.combat.boss_teleport_timer <= 0.0:
                    self.data.combat.boss_teleport_timer = 20.0
                    if len(self.enemy_crew) < 6 and self.data.player.ship.rooms:
                        t_r = random.choice(self.data.player.ship.rooms)
                        for _ in range(2):
                            self.enemy_crew.append(Crew(t_r.rect.centerx, t_r.rect.centery, name="Elite-Pirate", is_enemy=True))
                        self.show_message("WARNUNG! REBELLEN-BOARDER AUF DEIN SCHIFF TELEPORTIERT!")
                        if self.sound: self.sound.play("alarm")

        self.update_shields(dt)
        self.update_weapons(dt)
        self.update_enemy_weapon(dt)
        self.update_projectiles(dt)
        self.check_end_of_battle()

    def toggle_combat_drone(self):
        if getattr(self.data.combat, "combat_drone_active", False):
            self.data.combat.combat_drone_active = False
            self.show_message("KAMPFDROHNE DEAKTIVIERT!")
            return

        drone_room = next((r for r in self.data.player.ship.rooms if r.name == "Drohnen-Kontrolle"), None)
        power = drone_room.current_power if drone_room else 0
        if power < 1:
            self.show_message("DROHNEN-SYSTEM BRAUCHT MINDESTENS 1 ENERGIE!")
            return

        if self.data.player.drone_parts < 1:
            self.show_message("KEINE DROHNEN-TEILE MEHR!")
            return

        self.data.player.drone_parts -= 1
        self.data.combat.combat_drone_active = True
        self.data.combat.drone_fire_timer = 2.0
        if self.sound: self.sound.play("click")
        self.show_message("KAMPFDROHNE GESTARTET! (-1 Drohnen-Teil)")

    def toggle_repair_drone(self):
        if getattr(self.data.combat, "repair_drone_active", False):
            self.data.combat.repair_drone_active = False
            self.show_message("REPARATURDROHNE DEAKTIVIERT!")
            return

        drone_room = next((r for r in self.data.player.ship.rooms if r.name == "Drohnen-Kontrolle"), None)
        power = drone_room.current_power if drone_room else 0
        if power < 2:
            self.show_message("REPARATURDROHNE BRAUCHT MINDESTENS 2 ENERGIE!")
            return

        if self.data.player.drone_parts < 1:
            self.show_message("KEINE DROHNEN-TEILE MEHR!")
            return

        self.data.player.drone_parts -= 1
        self.data.combat.repair_drone_active = True
        if self.sound: self.sound.play("click")
        self.show_message("REPARATURDROHNE GESTARTET! (-1 Drohnen-Teil)")

    def update_crew(self, dt: float):
        # Automatisierte Relais & Sauerstoff-Konverter Augmentations
        augments = getattr(self.data.player, "augments", [])
        if "Automatisierte Relais" in augments:
            for r in self.data.player.ship.rooms:
                if r.health < r.max_health and r.fire_level == 0.0 and not r.has_breach:
                    r.repair(4.5 * dt)
        if "Sauerstoff-Konverter" in augments:
            for r in self.data.player.ship.rooms:
                if r.current_power > 0:
                    r.oxygen = min(100.0, r.oxygen + 2.5 * dt)

        # Sauerstoff & Erstickungs-Schaden (SRS Kap. 5.1)
        for room in self.data.player.ship.rooms:
            room.update_oxygen(dt, self.data.player.ship.rooms)
        for room in self.data.enemy.ship.rooms:
            room.update_oxygen(dt, self.data.enemy.ship.rooms)

        dead_crew: list = []
        for crew in self.data.player.crew:
            target_rooms = self.data.enemy.ship.rooms if crew.is_boarding else self.data.player.ship.rooms
            crew.update(dt, target_rooms)
            # Erstickungs- & Feuerschaden
            if crew.current_room:
                if crew.current_room.oxygen < 20.0:
                    asphyx_mod = 0.5 if getattr(crew, "trait", "") == "Sauerstoff-Sparer" else 1.0
                    crew.hp = max(0.0, crew.hp - 8.0 * asphyx_mod * dt)
                if crew.current_room.fire_level > 0.0:
                    crew.hp = max(0.0, crew.hp - (14.0 * crew.current_room.fire_level / 100.0) * dt)
            # Medbay-Heilung: Crew in eigener Medbay wird geheilt wenn Raum Strom hat
            if not crew.is_boarding and crew.current_room and crew.current_room.name == "Medbay" and crew.current_room.current_power > 0:
                heal_rate = 15.0 * crew.current_room.current_power
                crew.hp = min(crew.max_hp, crew.hp + heal_rate * dt)
            # Tod prüfen
            if crew.hp <= 0.0:
                dead_crew.append(crew)

        for dead in dead_crew:
            self.data.player.crew.remove(dead)
            if self.sound:
                self.sound.play("crew_death")
            self.show_message(f"CREW-MITGLIED {dead.name.upper()} GEFALLEN!")
        # Gegnerische Crew initialisieren & updaten (Ausgewogene Anzahl nach Sektor)
        if not self.enemy_crew and len(self.data.enemy.ship.rooms) > 0:
            sector = self.data.world.star_map.sector
            is_boss = "Boss" in self.data.enemy.ship.name or "Flaggschiff" in self.data.enemy.ship.name
            crew_count = 3 if is_boss else (2 if sector >= 2 else 1)
            target_rooms = self.data.enemy.ship.rooms[:crew_count]
            for r in target_rooms:
                self.enemy_crew.append(Crew(r.rect.centerx, r.rect.centery, name="Pirate", is_enemy=True))

        enemy_rooms = self.data.enemy.ship.rooms
        boarders = [c for c in self.data.player.crew if getattr(c, "is_boarding", False)]
        dead_enemy: list = []
        for e_crew in self.enemy_crew:
            e_crew.update(dt, enemy_rooms)
            if e_crew.hp <= 0.0:
                dead_enemy.append(e_crew)
                continue

            # Falls feindliches Crewmitglied am Ort steht -> Notfall-Aktionen (Feuer/Reparatur)
            if not e_crew.target_pos and e_crew.current_room:
                if e_crew.current_room.fire_level > 0.0:
                    e_crew.current_room.fire_level = max(0.0, e_crew.current_room.fire_level - 25.0 * dt)
                elif e_crew.current_room.health < e_crew.current_room.max_health:
                    e_crew.current_room.repair(20.0 * e_crew.repair_multiplier * dt)

            # KI Navigations-Triage (falls kein Bewegungsziel gesetzt)
            if not e_crew.target_pos:
                # 1. Geenterter Raum mit Enterern?
                boarded_room = next((b.current_room for b in boarders if b.current_room and b.current_room.is_enemy), None)
                if boarded_room and e_crew.current_room != boarded_room:
                    e_crew.target_pos = (boarded_room.rect.centerx, boarded_room.rect.centery)
                # 2. Brennender Raum?
                elif any(r.fire_level > 0 for r in enemy_rooms):
                    burning_room = next(r for r in enemy_rooms if r.fire_level > 0)
                    if e_crew.current_room != burning_room:
                        e_crew.target_pos = (burning_room.rect.centerx, burning_room.rect.centery)
                # 3. Beschädigter Raum?
                elif any(r.health < r.max_health for r in enemy_rooms):
                    damaged_room = next(r for r in enemy_rooms if r.health < r.max_health)
                    if e_crew.current_room != damaged_room:
                        e_crew.target_pos = (damaged_room.rect.centerx, damaged_room.rect.centery)
                # 4. Freie Station bemannen (Waffen, Schild, Brücke)
                else:
                    stations = [r for r in enemy_rooms if r.name in ("Brücke", "Waffen", "Schild")]
                    if stations:
                        station = random.choice(stations)
                        if e_crew.current_room != station and random.random() < 0.05:
                            e_crew.target_pos = (station.rect.centerx, station.rect.centery)

        for dead in dead_enemy:
            self.enemy_crew.remove(dead)

        # ------------------------------------------------------
        # NAHKAMPF & SYSTEM-SABOTAGE (Melee Combat & Sabotage)
        # ------------------------------------------------------
        all_rooms = self.data.player.ship.rooms + self.data.enemy.ship.rooms
        for r in all_rooms:
            p_in_r = [c for c in self.data.player.crew if c.current_room == r]
            e_in_r = [c for c in self.enemy_crew if c.current_room == r]

            # Nahkampf wenn beide Parteien im selben Raum stehen
            if p_in_r and e_in_r:
                for p_c in p_in_r:
                    for e_c in e_in_r:
                        p_c.hp = max(0.0, p_c.hp - 18.0 * e_c.melee_multiplier * dt)
                        e_c.hp = max(0.0, e_c.hp - 18.0 * p_c.melee_multiplier * dt)

            # Sabotage wenn eigene Enter-Crew in unverteidigtem gegnerischen Raum steht
            elif r.is_enemy and p_in_r and not e_in_r:
                r.apply_damage(12.0 * dt, self.data.enemy.reactor)
                self.data.enemy.ship.hp = max(0, self.data.enemy.ship.hp - int(1 * dt))
            elif not r.is_enemy and e_in_r and not p_in_r:
                r.apply_damage(12.0 * dt, self.data.player.reactor)
                self.data.player.ship.hp = max(0, self.data.player.ship.hp - int(1 * dt))

    def teleport_selected_crew_to_room(self, target_room):
        selected_crew = [c for c in self.data.player.crew if c.selected]
        if not selected_crew:
            tp_room = next((r for r in self.data.player.ship.rooms if r.name == "Teleporter"), None)
            if tp_room:
                selected_crew = [c for c in self.data.player.crew if c.current_room == tp_room]

        if not selected_crew:
            self.show_message("KEINE CREW ZUM ENTERN AUSGEWÄHLT!")
            return

        for c in selected_crew:
            c.is_boarding = True
            c.x = float(target_room.rect.centerx)
            c.y = float(target_room.rect.centery)
            c.target_pos = None
            c.current_room = target_room
            c.selected = False

        self.data.combat.teleport_cooldown = 12.0
        self.data.combat.is_teleport_targeting = False
        if self.sound: self.sound.play("click")
        self.show_message(f"{len(selected_crew)} CREW-MITGLIEDER AUFS GEGNERSCHIFF GEBEAMT!")

    def recall_boarding_crew(self):
        boarders = [c for c in self.data.player.crew if getattr(c, "is_boarding", False)]
        if not boarders:
            self.show_message("KEINE CREW AUF DEM GEGNERSCHIFF!")
            return

        dest_room = next((r for r in self.data.player.ship.rooms if r.name in ("Medbay", "Teleporter")), self.data.player.ship.rooms[0])
        for c in boarders:
            c.is_boarding = False
            c.x = float(dest_room.rect.centerx)
            c.y = float(dest_room.rect.centery)
            c.target_pos = None
            c.current_room = dest_room
            c.selected = False

        self.data.combat.teleport_cooldown = 12.0
        if self.sound: self.sound.play("click")
        self.show_message("ENTER-CREW ZURÜCKGEBEAMT!")

    def recall_boarding_crew_silent(self):
        dest_room = next((r for r in self.data.player.ship.rooms if r.name in ("Medbay", "Teleporter")), self.data.player.ship.rooms[0])
        for c in self.data.player.crew:
            if getattr(c, "is_boarding", False):
                c.is_boarding = False
                c.x = float(dest_room.rect.centerx)
                c.y = float(dest_room.rect.centery)
                c.target_pos = None
                c.current_room = dest_room
                c.selected = False


    def update_shields(self, dt: float):

        self.data.player.shield.update(
            dt,
            self.data.player.ship.rooms[0].current_power
        )

        self.data.enemy.shield.update(
            dt,
            self.data.enemy.ship.rooms[0].current_power
        )

    def update_weapons(self, dt: float):

        weapon_powered = (
            self.data.player.ship.rooms[1].current_power > 0
        )

        # Waffen-Bemannungsbonus (falls Crew in Waffenraum steht)
        weapon_manned = any(
            c.current_room == self.data.player.ship.rooms[1] for c in self.data.player.crew
        )
        charge_mult = 1.25 if weapon_manned else 1.0

        for weapon in self.data.player.weapons:
            weapon.update(dt * charge_mult, weapon_powered)

        if self.data.combat.autofire_enabled:
            self.fire_autofire_weapons()

    def fire_autofire_weapons(self):

        weapon_room = self.data.player.ship.rooms[1]

        for idx, weapon in enumerate(self.data.player.weapons):

            if not weapon.is_ready():
                continue

            if idx not in self.data.combat.weapon_targets:
                continue

            target_room, _, end_pos = \
                self.data.combat.weapon_targets[idx]

            if target_room not in self.data.enemy.ship.rooms:
                continue

            if (
                weapon.ammo_cost > 0
                and self.data.player.missiles < weapon.ammo_cost
            ):
                self.state_manager.show_message("KEINE RAKETEN MEHR!")
                continue

            if weapon.ammo_cost > 0:
                self.data.player.missiles -= weapon.ammo_cost

            slots = getattr(self.data.player.ship, "weapon_slots", [])
            start_pos = slots[idx]["pos"] if (slots and idx < len(slots)) else weapon_room.rect.center

            self.data.player.projectiles.append(
                Projectile(
                    start_pos,
                    end_pos,
                    target_room,
                    is_player_shot=True,
                    w_type=weapon.w_type,
                    shield_pierce=weapon.shield_pierce,
                    damage=weapon.damage,
                )
            )

            # Sound: weapon fire
            if self.sound:
                sfx = {"LASER": "laser_fire", "MISSILE": "missile_fire",
                       "BEAM": "beam_fire", "FLAK": "flak_fire",
                       "HEAVY_LASER": "laser_fire"}.get(weapon.w_type, "laser_fire")
                self.sound.play(sfx)

            weapon.reset()

    def activate_cloaking(self):
        cloak_room = next((r for r in self.data.player.ship.rooms if r.name == "Tarnung"), None)
        if not cloak_room:
            self.show_message("KEIN TARNSYSTEM VORHANDEN!")
            return

        if cloak_room.current_power <= 0:
            self.show_message("TARNSYSTEM HAT KEINE ENERGIE!")
            return

        if getattr(self.data.combat, "cloak_cooldown", 0.0) > 0.0 or getattr(self.data.combat, "cloak_active_timer", 0.0) > 0.0:
            self.show_message(f"TARNUNG LÄDT NOCH ({int(self.data.combat.cloak_cooldown)}s)!")
            return

        duration = 5.0 * cloak_room.current_power
        self.data.combat.cloak_active_timer = duration
        self.data.combat.cloak_cooldown = duration + 15.0
        if self.sound: self.sound.play("click")
        self.show_message(f"TARNUNG AKTIVIERT ({int(duration)}s)! (+100% Ausweichen)")

    def update_enemy_weapon(self, dt: float):

        weapon = self.data.enemy.weapon

        is_cloaked = getattr(self.data.combat, "cloak_active_timer", 0.0) > 0.0
        effective_dt = 0.0 if is_cloaked else dt

        enemy_weapon_manned = any(
            c.current_room and c.current_room.name == "Waffen" for c in self.enemy_crew
        )
        manned_mult = 1.20 if enemy_weapon_manned else 1.0

        weapon.update(
            effective_dt * manned_mult,
            self.data.enemy.ship.rooms[1].current_power > 0
            and self.data.enemy.ship.rooms[1].health > 20
        )

        if not weapon.is_ready():
            return

        target_room = random.choice(self.data.player.ship.rooms)
        enemy_slots = getattr(self.data.enemy.ship, "weapon_slots", [])
        enemy_start = enemy_slots[0]["pos"] if enemy_slots else self.data.enemy.ship.rooms[1].rect.center

        self.data.player.projectiles.append(
            Projectile(
                enemy_start,
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

        for projectile in self.data.player.projectiles[:]:

            projectile.update(dt)

            if projectile.alive:
                continue

            if projectile.is_player_shot:
                self.handle_player_hit(projectile)
            else:
                self.handle_enemy_hit(projectile)

            self.data.player.projectiles.remove(projectile)

    def handle_player_hit(self, projectile: Projectile):
        if getattr(self.data.combat, "zoltan_shield_hp", 0) > 0:
            self.data.combat.zoltan_shield_hp = max(0, self.data.combat.zoltan_shield_hp - 1)
            if self.sound: self.sound.play("shield_hit")
            self.show_message(f"ZOLTAN SUPER-SCHILD ABSORBIERT TREFFER! ({self.data.combat.zoltan_shield_hp} HP übrig)")
            return

        # SRS 6.2 Evasion Berechnung
        base_engine = self.data.enemy.ship.rooms[2].current_power * 0.10 if len(self.data.enemy.ship.rooms) > 2 else 0.10
        enemy_evade = base_engine

        if random.random() < enemy_evade:
            self.show_message("FEIND IST AUSGEWICHEN!")
        else:
            hit_successful = False
            if projectile.w_type in ("MISSILE", "BOMB"):
                hit_successful = True
            elif projectile.w_type == "ION":
                if self.data.enemy.shield.current_layers > 0:
                    self.data.enemy.shield.attempt_block()
                    self.data.enemy.shield.lock_timer = 5.0
                    self.show_message("GEGNERISCHES SCHILD IONISIERT (Sperre 5s)!")
                else:
                    projectile.target_room.ion_timer = 6.0
                    self.show_message(f"GEGNER-RAUM {projectile.target_room.name.upper()} IONISIERT (Sperre 6s)!")
            elif projectile.w_type == "BEAM":
                if self.data.enemy.shield.current_layers <= projectile.shield_pierce:
                    hit_successful = True
                else:
                    self.data.enemy.shield.attempt_block()
                    if self.sound: self.sound.play("shield_hit")
            else:
                if not self.data.enemy.shield.attempt_block():
                    hit_successful = True
                else:
                    if self.sound: self.sound.play("shield_hit")

            if hit_successful:
                if self.sound: self.sound.play("hull_hit")
                if projectile.w_type == "BOMB":
                    self.show_message(f"BOMBE DETONIERT IN {projectile.target_room.name.upper()}!")
                    if "Feuer" in getattr(projectile, "name", "") or projectile.damage == 0:
                        projectile.target_room.fire_level = min(100.0, projectile.target_room.fire_level + 65.0)
                    elif "Hüllenbruch" in getattr(projectile, "name", "") or projectile.damage == 15:
                        projectile.target_room.has_breach = True
                        projectile.target_room.apply_damage(40.0, self.data.enemy.reactor)
                        self.data.enemy.ship.hp = max(0, self.data.enemy.ship.hp - 1)
                    else:
                        projectile.target_room.apply_damage(30.0, self.data.enemy.reactor)
                        self.data.enemy.ship.hp = max(0, self.data.enemy.ship.hp - 1)
                elif projectile.w_type == "BEAM":
                    intersected_rooms = projectile.get_intersected_rooms(self.data.enemy.ship.rooms)
                    for room in intersected_rooms:
                        self.data.enemy.ship.hp = max(0, self.data.enemy.ship.hp - 1)
                        room.apply_damage(projectile.damage, self.data.enemy.reactor)
                else:
                    self.data.enemy.ship.hp = max(0, self.data.enemy.ship.hp - 1)
                    projectile.target_room.apply_damage(projectile.damage, self.data.enemy.reactor)

    def handle_enemy_hit(self, projectile: Projectile):
        if getattr(self.data.combat, "cloak_active_timer", 0.0) > 0.0:
            self.show_message("AUSGEWICHEN (TARNUNG)!")
            return
        # SRS 6.2 Evasion Formel: E = (E_Base_Engine + C_Engine_Bonus + C_Pilot_Bonus) * A_Multiplier + S_Cloak
        e_base_engine = self.data.player.ship.rooms[2].current_power * 0.10 if len(self.data.player.ship.rooms) > 2 else 0.10
        bridge_power = self.data.player.ship.rooms[2].current_power if len(self.data.player.ship.rooms) > 2 else 0
        pilot_present = any(c.current_room == self.data.player.ship.rooms[2] for c in self.data.player.crew)
        if pilot_present:
            a_multiplier = 1.0
        elif bridge_power >= 3:
            a_multiplier = 0.80
        elif bridge_power == 2:
            a_multiplier = 0.50
        else:
            a_multiplier = 0.0

        c_pilot_bonus = 0.10 if pilot_present else 0.0
        c_engine_bonus = 0.05 if any(c.current_room == self.data.player.ship.rooms[0] for c in self.data.player.crew) else 0.0
        s_cloak = 0.0

        player_evade = (e_base_engine + c_engine_bonus + c_pilot_bonus) * a_multiplier + s_cloak

        if random.random() < player_evade:
            self.show_message("AUSGEWICHEN!")
        else:
            hit_successful = False
            if projectile.w_type in ("MISSILE", "BOMB"):
                hit_successful = True
            elif projectile.w_type == "ION":
                if self.data.player.shield.current_layers > 0:
                    self.data.player.shield.attempt_block()
                    self.data.player.shield.lock_timer = 5.0
                    self.show_message("SCHILD IONISIERT (Sperre 5s)!")
                else:
                    projectile.target_room.ion_timer = 6.0
                    self.show_message(f"RAUM {projectile.target_room.name.upper()} IONISIERT (Sperre 6s)!")
            elif projectile.w_type == "BEAM":
                if self.data.player.shield.current_layers <= projectile.shield_pierce:
                    hit_successful = True
                else:
                    self.data.player.shield.attempt_block()
                    if self.sound: self.sound.play("shield_hit")
            else:
                if not self.data.player.shield.attempt_block():
                    hit_successful = True
                else:
                    if self.sound: self.sound.play("shield_hit")

            if hit_successful:
                if self.sound: self.sound.play("hull_hit")
                if projectile.w_type == "BOMB":
                    self.show_message(f"BOMBE DETONIERT IN DEINEM {projectile.target_room.name.upper()}!")
                    projectile.target_room.fire_level = min(100.0, projectile.target_room.fire_level + 50.0)
                    projectile.target_room.apply_damage(25.0, self.data.player.reactor)
                    self.data.player.ship.hp = max(0, self.data.player.ship.hp - 1)
                elif projectile.w_type == "BEAM":
                    intersected_rooms = projectile.get_intersected_rooms(self.data.player.ship.rooms)
                    for room in intersected_rooms:
                        self.data.player.ship.hp = max(0, self.data.player.ship.hp - 1)
                        room.apply_damage(projectile.damage, self.data.player.reactor)
                        for crew in self.data.player.crew:
                            if crew.current_room == room:
                                crew.hp = max(0.0, crew.hp - 15.0)
                else:
                    self.data.player.ship.hp = max(0, self.data.player.ship.hp - 1)
                    projectile.target_room.apply_damage(projectile.damage, self.data.player.reactor)
                    for crew in self.data.player.crew:
                        if crew.current_room == projectile.target_room:
                            crew.hp = max(0.0, crew.hp - 20.0)


    def check_end_of_battle(self):
        if self.data.enemy.ship.hp <= 0:
            if "Flaggschiff" in getattr(self.data.enemy.ship, "name", ""):
                b_phase = getattr(self.data.combat, "boss_phase", 1)
                if b_phase == 1:
                    self.data.combat.boss_phase = 2
                    self.data.enemy.ship.hp = 35
                    self.data.enemy.ship.max_hp = 35
                    self.data.enemy.weapon = Weapon("Schwarm-Laser (Phase 2)", charge_time=3.2, w_type="LASER", damage=35.0)
                    for r in self.data.enemy.ship.rooms:
                        r.health = r.max_health
                        r.fire_level = 0.0
                        r.has_breach = False
                    if self.sound: self.sound.play("explosion")
                    self.show_message("PHASE 1 ZERSTÖRT! FLAGGSCHIFF WECHSELT IN PHASE 2 (DROHNENSCHWARM)!")
                    return
                elif b_phase == 2:
                    self.data.combat.boss_phase = 3
                    self.data.enemy.ship.hp = 40
                    self.data.enemy.ship.max_hp = 40
                    self.data.combat.zoltan_shield_hp = 12
                    self.data.enemy.weapon = Weapon("Super-Artillerie (Phase 3)", charge_time=3.8, w_type="HEAVY_LASER", damage=50.0)
                    for r in self.data.enemy.ship.rooms:
                        r.health = r.max_health
                        r.fire_level = 0.0
                        r.has_breach = False
                    if self.sound: self.sound.play("explosion")
                    self.show_message("PHASE 2 ZERSTÖRT! PHASE 3 AKTIVIERT (ZOLTAN SUPER-SCHILD)!")
                    return

            if self.sound: self.sound.play("explosion")
            self.recall_boarding_crew_silent()
            self.player_won()
            return

        # Schiffs-Kaperung (Enemy crew completely eliminated by boarding)
        if len(self.enemy_crew) == 0 and len(self.data.player.crew) > 0 and self.data.current_state == STATE_COMBAT:
            self.show_message("SCHIFF GEKAPERT! Feindliche Crew eliminiert (+BONUS BEUTE)!")
            self.data.player.scrap += 35
            self.data.player.fuel += 2
            self.recall_boarding_crew_silent()
            self.player_won()
            return

        if self.data.player.ship.hp <= 0 or len(self.data.player.crew) == 0:
            if self.sound: self.sound.play("game_over")
            self.player_lost()

    def calculate_stochastic_rewards(self, reward_tier: str = "Medium") -> tuple[int, int]:
        """SRS 6.3 Stochastische Belohnungsberechnung: Scrap = floor(B_Sector * V_Tier)."""
        sector = self.data.world.star_map.sector
        b_sector = 15 + sector * 10
        if reward_tier == "Low":
            v_tier = random.uniform(0.5, 0.7)
        elif reward_tier == "High":
            v_tier = random.uniform(1.3, 1.55)
        else:  # Medium
            v_tier = random.uniform(0.8, 1.3)

        scrap = int(b_sector * v_tier)
        if "Schrott-Arm" in getattr(self.data.player, "augments", []):
            scrap = int(scrap * 1.30)
        missiles = random.randint(1, 3)

        # 3% bis 6% Chance auf Bonus-Drop (SRS Kap. 6.3)
        drop_chance = 0.06 if reward_tier == "High" else 0.03
        if random.random() < drop_chance:
            self.data.player.missiles += 2
            self.show_message("BONUS-BEUTE GEFUNDEN! (+2 Raketen)")

        return scrap, missiles

    def player_won(self):

        is_mini_boss = "Mini-Boss" in self.data.enemy.ship.name
        is_final_boss = "Flaggschiff" in self.data.enemy.ship.name or (self.data.world.star_map.sector >= 5 and not is_mini_boss)
        tier = "High" if (is_final_boss or is_mini_boss) else "Medium"
        scrap_reward, missile_reward = self.calculate_stochastic_rewards(tier)

        self.data.player.scrap += scrap_reward
        self.data.player.missiles += missile_reward
        self.enemy_crew.clear()

        self.data.player.projectiles.clear()
        self.data.combat.weapon_targets.clear()

        from managers.save_manager import SaveManager
        ship_sequence = ["Kestrel", "Kreuzer", "Tarnschiff", "Zoltan-Fregatte", "Federations-Kreuzer"]
        unlocked = SaveManager.load_unlocks()
        new_ship = None
        for s in ship_sequence:
            if s not in unlocked:
                unlocked.append(s)
                new_ship = s
                SaveManager.save_unlocks(unlocked)
                break
        self.data.player.unlocked_ships = unlocked
        if new_ship:
            self.data.player.newly_unlocked_ship = new_ship

        if is_final_boss:
            self.data.current_state = STATE_VICTORY
        elif is_mini_boss:
            sec = self.data.world.star_map.sector
            self.data.world.star_map.sector += 1
            self.data.world.star_map.generate_map()
            self.data.player.scrap += 25

            if new_ship:
                self.show_message(f"NEUES SCHIFF FREIGESCHALTET: {new_ship}!")
            else:
                self.show_message(f"MINI-BOSS BESIEGT! WEITER ZU SEKTOR {self.data.world.star_map.sector}")

            self.data.current_state = STATE_MAP
        else:
            self.data.current_state = STATE_MAP



    def player_lost(self):

        self.data.player.projectiles.clear()
        self.data.combat.weapon_targets.clear()
        self.enemy_crew.clear()

        self.data.current_state = STATE_GAME_OVER

    def show_message(self, text: str):

        self.data.combat.msg = text
        self.data.combat.msg_timer = 1.5

