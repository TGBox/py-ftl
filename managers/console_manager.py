import pygame

from classes.GameData import GameData
from settings import LOGICAL_HEIGHT, LOGICAL_WIDTH


class ConsoleManager:
    """In-game developer console and cheat code system (TODO 43)."""

    def __init__(self, data: GameData):
        self.data = data
        self.active: bool = False
        self.input_text: str = ""
        self.history: list[str] = [
            "--- ENTWICKLER-KONSOLE ---",
            "Tippe 'help' für eine Liste aller Cheat-Befehle.",
        ]
        self.party_mode: bool = False
        self.turbo_mode: bool = False
        self.sound = None  # Set by Game after construction

    def toggle(self):
        self.active = not self.active
        self.input_text = ""

    def handle_keydown(self, event: pygame.event.Event) -> bool:
        """Behandelt Tasteneingaben für die Konsole. Gibt True zurück, wenn die Eingabe konsumiert wurde."""
        if event.key in (pygame.K_BACKQUOTE, pygame.K_F12):
            self.toggle()
            return True

        if not self.active:
            return False

        if event.key == pygame.K_ESCAPE:
            self.active = False
            return True

        elif event.key == pygame.K_RETURN:
            cmd = self.input_text.strip()
            if cmd:
                self.history.append(f"> {cmd}")
                self.execute_command(cmd)
                self.input_text = ""
            return True

        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
            return True

        elif event.unicode and event.unicode.isprintable():
            if len(self.input_text) < 45:
                self.input_text += event.unicode
            return True

        return True

    def execute_command(self, cmd_str: str):
        parts = cmd_str.lower().split()
        if not parts:
            return

        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        if cmd == "help":
            self.history.extend([
                "VERFÜGBARE CHEATS:",
                "  scrap / geld [n]     - Scrap hinzufügen (+500)",
                "  waffen5 / mk5        - Waffen auf Level 5 (MK V) aufrüsten",
                "  fuel / treibstoff    - Treibstoff hinzufügen (+20)",
                "  missiles / raketen   - Raketen hinzufügen (+20)",
                "  drones / drohnen     - Drohnenteile hinzufügen (+20)",
                "  godmode / god        - Unverwundbarkeit umschalten",
                "  heal                 - Schiff & Crew komplett heilen",
                "  win                  - Gefecht sofort gewinnen",
                "  unlock_all           - Alle 8 Schiffe freischalten",
                "  party / turbo        - Fun-Cheats",
            ])

        elif cmd in ("scrap", "scraps", "money", "geld", "add_scrap", "add_scraps", "add_money"):
            val = int(arg) if arg and (arg.isdigit() or (arg.startswith("-") and arg[1:].isdigit())) else 500
            self.data.player.scrap += val
            self.history.append(f"[CHEAT] +{val} Scrap hinzugefügt! (Aktuell: {self.data.player.scrap})")

        elif cmd in ("upgrade_weapons", "max_weapons", "waffen5", "mk5", "level5", "waffen", "upgrade_all_weapons"):
            upgraded_count = 0
            for w in self.data.player.weapons:
                if w is not None:
                    while w.level < 5:
                        w.upgrade()
                    upgraded_count += 1
            self.history.append(f"[CHEAT] Alle {upgraded_count} aktiven Waffen auf Level 5 (MK V) aufgerüstet!")

        elif cmd in ("fuel", "treibstoff"):
            val = int(arg) if arg and arg.isdigit() else 20
            self.data.player.fuel += val
            self.history.append(f"[CHEAT] +{val} Treibstoff hinzugefügt! (Aktuell: {self.data.player.fuel})")

        elif cmd in ("missiles", "missile", "raketen"):
            val = int(arg) if arg and arg.isdigit() else 20
            self.data.player.missiles += val
            self.history.append(f"[CHEAT] +{val} Raketen hinzugefügt! (Aktuell: {self.data.player.missiles})")

        elif cmd in ("drones", "drone", "drohnen"):
            val = int(arg) if arg and arg.isdigit() else 20
            self.data.player.drone_parts += val
            self.history.append(f"[CHEAT] +{val} Drohnenteile hinzugefügt! (Aktuell: {self.data.player.drone_parts})")

        elif cmd in ("godmode", "god", "invincible"):
            cur = getattr(self.data.player, "godmode", False)
            self.data.player.godmode = not cur
            state_str = "AKTIVIERT" if not cur else "DEAKTIVIERT"
            self.history.append(f"[CHEAT] Godmode {state_str}!")

        elif cmd in ("heal", "repair_all"):
            self.data.player.ship.hp = self.data.player.ship.max_hp
            for c in self.data.player.crew:
                c.hp = c.max_hp
            for r in self.data.player.ship.rooms:
                r.health = r.max_health
                r.fire_level = 0.0
                r.has_breach = False
            self.history.append("[CHEAT] Schiff, Crew & Räume komplett geheilt!")

        elif cmd == "win":
            if self.data.current_state == "COMBAT" and getattr(self.data, "enemy", None) and getattr(self.data.enemy, "ship", None):
                self.data.enemy.ship.hp = 0
                self.history.append("[CHEAT] Gegnerschiff zerstört! Instant-Win ausgelöst.")
            else:
                self.history.append("[WARNUNG] Win-Cheat ist nur während eines aktiven Gefechts nutzbar.")

        elif cmd in ("unlock_all", "unlockall"):
            from managers.save_manager import SaveManager
            all_ships = [
                "Kestrel",
                "Kreuzer",
                "Tarnschiff",
                "Zoltan-Fregatte",
                "Federations-Kreuzer",
                "Mantis-Kaperer",
                "Rock-Schlachtschiff",
                "Kristall-Kreuzer",
            ]
            SaveManager.save_unlocks(all_ships)
            self.data.player.unlocked_ships = all_ships
            self.history.append("[CHEAT] Alle 8 Raumschiffe wurden erfolgreich freigeschaltet!")

        elif cmd == "party":
            self.party_mode = not self.party_mode
            setattr(self.data, "party_mode", self.party_mode)
            state_str = "AN 🎉" if self.party_mode else "AUS"
            self.history.append(f"[FUN-CHEAT] Disko-Party-Modus {state_str}!")

        elif cmd == "turbo":
            self.turbo_mode = not self.turbo_mode
            setattr(self.data, "turbo_mode", self.turbo_mode)
            state_str = "AN (2.5x Speed) ⚡" if self.turbo_mode else "AUS"
            self.history.append(f"[FUN-CHEAT] Turbo-Modus {state_str}!")

        else:
            self.history.append(f"[ERROR] Unbekannter Befehl: '{cmd}'. Tippe 'help' für Befehle.")

    def render(self, screen: pygame.Surface):
        if not self.active:
            return

        font = pygame.font.SysFont(None, 16)
        c_rect = pygame.Rect(50, 180, 800, 240)

        s = pygame.Surface((c_rect.width, c_rect.height), pygame.SRCALPHA)
        s.fill((10, 16, 26, 235))
        screen.blit(s, (c_rect.x, c_rect.y))
        pygame.draw.rect(screen, (0, 220, 255), c_rect, 2)

        # Letzte 9 Zeilen History anzeigen
        lines_to_draw = self.history[-9:]
        for idx, line in enumerate(lines_to_draw):
            col = (100, 255, 180) if line.startswith(">") else ((255, 220, 100) if line.startswith("[CHEAT]") else (200, 220, 245))
            surf = font.render(line, True, col)
            screen.blit(surf, (c_rect.x + 12, c_rect.y + 10 + idx * 20))

        # Eingabezeile unten
        pygame.draw.line(screen, (0, 180, 230), (c_rect.x + 10, c_rect.y + 205), (c_rect.x + c_rect.width - 10, c_rect.y + 205), 1)
        prompt_txt = f"> {self.input_text}_"
        p_surf = font.render(prompt_txt, True, (0, 255, 200))
        screen.blit(p_surf, (c_rect.x + 12, c_rect.y + 212))
