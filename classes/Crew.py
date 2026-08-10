from typing import TYPE_CHECKING


from collections import deque
import math
import pygame
import random

from classes.Door import Door
from classes.Room import Room
from managers.achievement_manager import AchievementManager
from settings import *

if TYPE_CHECKING:
    from classes.GameData import GameData
    from game import Game
    from managers.combat_manager import CombatManager

SPECIES_NAMES = {
    "Mensch": ["Vance", "Sarah", "Jackson", "Elena", "Marcus", "David", "Lisa", "Alex"],
    "Engi": ["Slockat", "Tuco", "Kaz", "01-Beta", "Xix", "N-402", "Kael"],
    "Mantis": ["Kazaak", "Ruwen", "Skraak", "Zazz", "Kazaakth", "Voraak"],
}

CREW_TRAITS = ["Sprinter", "Sauerstoff-Sparer", "Feuerwehr", "Kampfveteran"]


def find_room_path(
    start_room: Room, target_room: Room, rooms: list[Room], doors: list[Door]
) -> list[tuple[Room, Door]]:
    """BFS shortest path of (next_room, door) from start_room to target_room."""
    if start_room == target_room:
        return []

    adj: dict[Room, list[tuple[Room, Door]]] = {r: [] for r in rooms}
    for d in doors:
        if not d.is_airlock and d.room_a in adj and d.room_b in adj and d.room_b is not None: # type: ignore
            adj[d.room_a].append((d.room_b, d))
            adj[d.room_b].append((d.room_a, d))

    queue = deque([start_room])
    visited: dict[Room, tuple[Room, Door] | None] = {start_room: None}

    found = False
    while queue:
        curr = queue.popleft()
        if curr == target_room:
            found = True
            break
        for neighbor, door in adj.get(curr, []):
            if neighbor not in visited:
                visited[neighbor] = (curr, door)
                queue.append(neighbor)

    if not found:
        return []

    path: list[tuple[Room, Door]] = []
    curr = target_room
    while curr != start_room:
        prev = visited[curr]
        if prev is None:
            break
        parent_room, door = prev
        path.append((curr, door))
        curr = parent_room

    path.reverse()
    return path


class Crew:

    def __init__(
        self,
        x: float,
        y: float,
        name: str = "",
        species: str = "Mensch",
        is_enemy: bool = False,
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.radius: int = 12
        self.selected: bool = False
        self.target_pos: tuple[int, int] | None = None
        self.path_waypoints: list[tuple[float, float]] = []
        self.species: str = species
        self.name: str = name if name else random.choice(SPECIES_NAMES.get(species, ["Crew"]))
        self.is_enemy: bool = is_enemy
        self.hp: float = 100.0
        self.max_hp: float = 100.0
        self.current_room: Room | None = None
        self.trait: str = random.choice(CREW_TRAITS)
        self.variant_idx: int = random.randint(0, 2)
        self.anim_timer: float = random.uniform(0.0, 5.0)

        self.is_boarding: bool = False
        self.stun_timer: float = 0.0

        # Trainings-Skills (Stufe 0 bis 3)
        self.skill_repair: int = 0
        self.skill_combat: int = 0
        self.skill_piloting: int = 0
        self.skill_fitness: int = 0

        # Spezies-Eigenschaften & Aktive Fähigkeiten
        self.ability_cooldown: float = 0.0
        self.ability_active_timer: float = 0.0

        if self.species == "Engi":
            self.repair_multiplier: float = 2.0
            self.melee_multiplier: float = 0.5
            self.ability_name: str = "Schnell-Reparatur"
            self.max_ability_cooldown: float = 15.0
        elif self.species == "Mantis":
            self.repair_multiplier: float = 0.6
            self.melee_multiplier: float = 2.0
            self.ability_name: str = "Kampfrausch"
            self.max_ability_cooldown: float = 20.0
        elif self.species == "Rock":
            self.repair_multiplier: float = 1.0
            self.melee_multiplier: float = 1.2
            self.ability_name: str = "Erderschütterung"
            self.max_ability_cooldown: float = 25.0
        elif self.species == "Zoltan":
            self.repair_multiplier: float = 1.0
            self.melee_multiplier: float = 0.8
            self.ability_name: str = "Schild-Burst"
            self.max_ability_cooldown: float = 20.0
        else:  # Mensch / standard
            self.repair_multiplier: float = 1.0
            self.melee_multiplier: float = 1.0
            self.ability_name: str = "Taktischer Fokus"
            self.max_ability_cooldown: float = 15.0

        if self.trait == "Feuerwehr":
            self.repair_multiplier *= 1.4
        elif self.trait == "Kampfveteran":
            self.melee_multiplier += 0.3

        self.move_speed: float = 160.0 if self.trait == "Sprinter" else 120.0
        
    def to_str(self) -> str:
        """Methode um aus dem Crew Objekt eine von Menschen gut lesbare String Repräsentation zu generieren.

        Returns:
            str: Die String Repräsentation dieses Crew Objekts.
        """
        c_str = f"{"Gegner" if self.is_enemy else "Spieler"} Crewmitglied \"{self.name}\" der Spezies {self.species} mit der Eigenschaft {self.trait}. Gesundheit: {self.hp} / {self.max_hp}, Position: x={self.x}, y={self.y}, Geschwindigkeit: {self.move_speed}, Radius: {self.radius}.\n"
        c_str += f"Ausgewählt: {self.selected}, Raum: {"Keiner" if self.current_room is None else self.current_room.name}, Zielposition: "
        if self.target_pos is None:
            c_str += "Keine, "
        else:
            c_str += f"x={self.target_pos[0]}, y={self.target_pos[1]}, "
        c_str += "Zielwegpunkte: "
        if len(self.path_waypoints) == 0:
            c_str += "Keine, "
        else:
            for i, p in enumerate(self.path_waypoints):
                c_str += f"[{i}.) x={p[0]}, y={p[1]}], "
        c_str += f"Variante: {self.variant_idx}, Animationstimer: {self.anim_timer}, Stuntimer: {self.stun_timer}, Boarding: {self.is_boarding}\nAbilityName: {self.ability_name}, AbilityCooldown: {self.ability_cooldown}, AbilityMaxCooldown: {self.max_ability_cooldown}, AbilityActiveTimer: {self.ability_active_timer}"
        c_str += f"Skills - Reparatur: {self.skill_repair}, Pilot: {self.skill_piloting}, Kampf: {self.skill_combat}, Fitness: {self.skill_fitness}"
        return c_str

    def activate_ability(self, data: "GameData", game: "Game", combat_mgr: "CombatManager | None" = None) -> bool:
        if self.ability_cooldown > 0.0:
            if combat_mgr:
                combat_mgr.show_message(f"{self.name.upper()} FÄHIGKEIT LÄDT NOCH ({int(self.ability_cooldown)}s)!")
            return False

        self.ability_cooldown = self.max_ability_cooldown
        sound = getattr(combat_mgr, "sound", None)

        if self.species == "Engi":
            if self.current_room:
                self.current_room.health = min(self.current_room.max_health, self.current_room.health + 35.0)
                self.current_room.fire_level = 0.0
                self.current_room.has_breach = False
                if sound: sound.play("repair")
                if combat_mgr: combat_mgr.show_message(f"{self.name.upper()} HAT {self.current_room.name.upper()} SOFORT REPARIERT!")

        elif self.species == "Mantis":
            self.ability_active_timer = 8.0
            if sound: sound.play("click")
            if combat_mgr: combat_mgr.show_message(f"{self.name.upper()} GEHT IN KAMPFRAUSCH (+100% Schaden)!")

        elif self.species == "Rock":
            if self.current_room:
                enemies_in_room = [e for e in getattr(combat_mgr, "enemy_crew", []) if e.current_room == self.current_room]
                for e in enemies_in_room:
                    e.stun_timer = 4.0
                if hasattr(game, "particle_manager"):
                    game.particle_manager.emit_explosion(self.x, self.y, count=15)
                if sound: sound.play("explosion")
                if combat_mgr: combat_mgr.show_message(f"{self.name.upper()} ERDERSCHÜTTERUNG! Gegner stunnt (4s)!")

        elif self.species == "Zoltan":
            shield_max = max(1, getattr(data.player.shield, "max_layers", 1))
            data.player.shield.current_layers = min(shield_max, data.player.shield.current_layers + 1)
            if hasattr(game, "particle_manager"):
                game.particle_manager.emit_shield_ripple(self.x, self.y, (100, 255, 140))
            if sound: sound.play("shield_recharge")
            if combat_mgr: combat_mgr.show_message(f"{self.name.upper()} SCHILD-BURST! +1 Schildschicht wiederhergestellt!")

        else:  # Mensch
            if self.current_room:
                allies_in_room = [c for c in data.player.crew if c.current_room == self.current_room]
                for c in allies_in_room:
                    c.hp = min(c.max_hp, c.hp + 25.0)
                if sound: sound.play("click")
                if combat_mgr: combat_mgr.show_message(f"{self.name.upper()} TAKTISCHER FOKUS! Crew geheilt (+25 HP)!")

        return True

    def train_skill(self, skill_name: str, achievement_manager: AchievementManager | None = None) -> bool:
        if skill_name == "repair" and self.skill_repair < 3:
            self.skill_repair += 1
            self.repair_multiplier *= 1.25
            if self.skill_repair == 3 and achievement_manager:
                achievement_manager.unlock("master_mechanic")
            return True
        elif skill_name == "combat" and self.skill_combat < 3:
            self.skill_combat += 1
            self.melee_multiplier *= 1.30
            if self.skill_combat == 3 and achievement_manager:
                achievement_manager.unlock("master_warrior")
            return True
        elif skill_name == "piloting" and self.skill_piloting < 3:
            self.skill_piloting += 1
            return True
        elif skill_name == "fitness" and self.skill_fitness < 3:
            self.skill_fitness += 1
            self.max_hp += 15.0
            self.hp = min(self.max_hp, self.hp + 15.0)
            return True
        return False

    def recalculate_path(self, rooms: list[Room], doors: list[Door]) -> None:
        if not self.target_pos:
            self.path_waypoints = []
            return

        tx, ty = float(self.target_pos[0]), float(self.target_pos[1])

        start_room = self.current_room
        if not start_room:
            for room in rooms:
                if room.rect.collidepoint(int(self.x), int(self.y)):
                    start_room = room
                    break

        target_room = None
        for room in rooms:
            if room.rect.collidepoint(int(tx), int(ty)):
                target_room = room
                break

        if not start_room or not target_room or start_room == target_room:
            self.path_waypoints = [(tx, ty)]
            return

        room_path = find_room_path(start_room, target_room, rooms, doors)
        if not room_path:
            self.path_waypoints = [(tx, ty)]
            return

        waypoints: list[tuple[float, float]] = []
        for _, door in room_path:
            waypoints.append((float(door.rect.centerx), float(door.rect.centery)))
        waypoints.append((tx, ty))

        self.path_waypoints = waypoints

    def update(
        self, dt: float, rooms: list[Room], doors: list[Door] | None = None
    ) -> None:
        self.anim_timer += dt
        self.ability_cooldown = max(0.0, self.ability_cooldown - dt)
        self.ability_active_timer = max(0.0, self.ability_active_timer - dt)

        if self.species == "Mantis":
            self.melee_multiplier = 4.0 if self.ability_active_timer > 0.0 else 2.0

        ship_doors = doors if doors is not None else getattr(self, "ship_doors", [])

        if self.stun_timer > 0.0:
            self.stun_timer = max(0.0, self.stun_timer - dt)
            self.current_room = None
            for room in rooms:
                if room.rect.collidepoint(int(self.x), int(self.y)):
                    self.current_room = room
                    break
            return

        if self.target_pos:
            target_tuple = (float(self.target_pos[0]), float(self.target_pos[1]))
            if (
                not self.path_waypoints
                or self.path_waypoints[-1] != target_tuple
            ):
                self.recalculate_path(rooms, ship_doors)

            if self.path_waypoints:
                wx, wy = self.path_waypoints[0]
                dx, dy = wx - self.x, wy - self.y
                dist = math.hypot(dx, dy)
                step = self.move_speed * dt
                if dist <= step or dist < 1e-5:
                    self.x, self.y = float(wx), float(wy)
                    self.path_waypoints.pop(0)
                    if not self.path_waypoints:
                        self.target_pos = None
                else:
                    self.x += (dx / dist) * step
                    self.y += (dy / dist) * step

            # Innentüren beim Durchlaufen automatisch öffnen
            if ship_doors:
                for d in ship_doors:
                    if not d.is_airlock and d.rect.inflate(30, 30).collidepoint(int(self.x), int(self.y)):
                        if not d.is_open:
                            d.is_open = True
                            d.opened_by_crew = True

        self.current_room = None
        for room in rooms:
            if room.rect.collidepoint(int(self.x), int(self.y)):
                self.current_room = room
                if not self.target_pos and room.health < room.max_health:
                    room.repair(25.0 * self.repair_multiplier * dt)
                break

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        is_moving = self.target_pos is not None
        is_repairing = (not is_moving and self.current_room and self.current_room.health < self.current_room.max_health)
        is_manning = (not is_moving and not is_repairing and self.current_room and self.current_room.current_power > 0)

        # Lauf-Bobbing Y-Offset
        bob_y = math.sin(self.anim_timer * 14.0) * 3.0 if is_moving else 0.0
        draw_y = cy + int(bob_y)

        # 1. Spezies-Farben & Sprite-Merkmale
        if self.is_enemy:
            body_color = (240, 60, 60)
            detail_color = (120, 20, 20)
            visor_color = (255, 200, 100)
        elif self.species == "Engi":
            var_cols = [(100, 200, 255), (255, 200, 80), (200, 230, 255)]
            body_color = var_cols[self.variant_idx % 3]
            detail_color = (40, 60, 90)
            visor_color = (0, 255, 255)
        elif self.species == "Mantis":
            var_cols = [(140, 240, 80), (40, 180, 70), (220, 220, 60)]
            body_color = var_cols[self.variant_idx % 3]
            detail_color = (20, 80, 30)
            visor_color = (255, 60, 60)
        elif self.species == "Zoltan":
            var_cols = [(100, 255, 140), (100, 220, 255), (255, 230, 100)]
            body_color = var_cols[self.variant_idx % 3]
            detail_color = (255, 255, 255)
            visor_color = (255, 255, 255)
        elif self.species == "Rock":
            var_cols = [(180, 100, 60), (220, 80, 40), (120, 110, 100)]
            body_color = var_cols[self.variant_idx % 3]
            detail_color = (60, 35, 20)
            visor_color = (255, 180, 60)
        else:  # Mensch
            var_cols = [(60, 140, 240), (240, 240, 240), (120, 130, 160)]
            body_color = var_cols[self.variant_idx % 3]
            detail_color = (30, 50, 80)
            visor_color = (255, 220, 150)

        if self.selected:
            body_color = COLOR_SELECTED

        # Bemannungs-Pulsieren am Raumterminal
        if is_manning:
            pulse_r = int(14 + math.sin(self.anim_timer * 6.0) * 3)
            pygame.draw.circle(surface, (100, 220, 255, 150), (cx, draw_y), pulse_r, 1)

        # Haupt-Körper (Kopf & Torso Sprite)
        pygame.draw.circle(surface, body_color, (cx, draw_y), self.radius)
        pygame.draw.circle(surface, (255, 255, 255) if self.selected else (0, 0, 0), (cx, draw_y), self.radius, 1)

        # Spezies-spezifische Sprite-Details (Augen/Klauen/Sensoren)
        if self.species == "Mantis":
            # Klauen / Scythes
            pygame.draw.line(surface, visor_color, (cx - 8, draw_y - 4), (cx - 14, draw_y + 4), 2)
            pygame.draw.line(surface, visor_color, (cx + 8, draw_y - 4), (cx + 14, draw_y + 4), 2)
        elif self.species == "Engi":
            # Scanner-Visor
            pygame.draw.rect(surface, visor_color, (cx - 6, draw_y - 3, 12, 4))
        elif self.species == "Zoltan":
            # Energie-Aura Ring
            pygame.draw.circle(surface, (255, 255, 255), (cx, draw_y), self.radius + 3, 1)
        elif self.species == "Rock":
            # Schulterpanzer
            pygame.draw.circle(surface, detail_color, (cx - 9, draw_y + 2), 4)
            pygame.draw.circle(surface, detail_color, (cx + 9, draw_y + 2), 4)
        else:  # Mensch Visor / Cap
            pygame.draw.line(surface, visor_color, (cx - 4, draw_y - 2), (cx + 4, draw_y - 2), 2)

        # Reparatur-Animation: Schweißfunken & Werkzeugbewegung
        if is_repairing:
            arm_x = cx + int(math.sin(self.anim_timer * 18.0) * 6)
            arm_y = draw_y - 8
            pygame.draw.line(surface, (255, 240, 100), (cx, draw_y), (arm_x, arm_y), 2)

            for _ in range(2):
                sx = cx + random.randint(-12, 12)
                sy = draw_y + random.randint(-12, 12)
                spark_col = random.choice([(255, 240, 100), (100, 240, 255), (255, 255, 255)])
                pygame.draw.circle(surface, spark_col, (sx, sy), random.randint(1, 2))

        # Stun-Effekt Overlay (Funken um Crew-Mitglied)
        if self.stun_timer > 0.0:
            for _ in range(3):
                sx = cx + random.randint(-14, 14)
                sy = draw_y + random.randint(-14, 14)
                s_color = random.choice([(100, 240, 255), (255, 255, 100), (200, 220, 255)])
                pygame.draw.circle(surface, s_color, (sx, sy), random.randint(2, 4))
            stun_lbl = get_font(12, bold=True).render("STUN", True, (100, 240, 255))
            surface.blit(stun_lbl, (cx - stun_lbl.get_width() // 2, draw_y - self.radius - 16))

        # HP-Balken über dem Crewmitglied
        if self.hp < self.max_hp or self.selected:
            bar_w = 20
            bar_h = 3
            bar_x = cx - bar_w // 2
            bar_y = draw_y - self.radius - 6
            hp_ratio = max(0.0, self.hp / self.max_hp)
            pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surface, (50, 220, 100), (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

        # Spezies-Badge Buchstabe im Kreis
        badge_char = "P" if self.is_enemy else (self.species[0] if self.species else "C")
        badge_lbl = get_font(13, bold=True).render(badge_char, True, (0, 0, 0) if self.selected else (255, 255, 255))
        surface.blit(badge_lbl, (cx - badge_lbl.get_width() // 2, draw_y - badge_lbl.get_height() // 2))

        # Name & Trait-Badge zeichnen
        trait_str = f" [{self.trait[:4]}]" if hasattr(self, "trait") and self.trait else ""
        name_lbl = get_font(13).render(f"{self.name}{trait_str}", True, (255, 255, 255) if self.selected else (200, 210, 220))
        surface.blit(name_lbl, (cx - name_lbl.get_width() // 2, draw_y + self.radius + 2))