from typing import TYPE_CHECKING, Any

import json
import os
import time
import pygame

from managers.sound_manager import SoundManager

if TYPE_CHECKING:
    from game import Game

ACHIEVEMENT_FILE = "data/achievements.json"

ACHIEVEMENTS_MASTER = [
    # --- KAMPF & ZERSTÖRUNG ---
    {
        "id": "first_victory",
        "title": "Erster Sieg",
        "desc": "Besiege ein feindliches Raumschiff im Gefecht.",
        "category": "KAMPF",
    },
    {
        "id": "boss_slayer",
        "title": "Rebellen-Schreck",
        "desc": "Besiege einen Sektor Mini-Boss.",
        "category": "KAMPF",
    },
    {
        "id": "flagship_down",
        "title": "Galaktischer Retter",
        "desc": "Zerstöre das Endboss-Flaggschiff der Rebellen!",
        "category": "KAMPF",
    },
    {
        "id": "beam_master",
        "title": "Strahlungs-Spezialist",
        "desc": "Treffe 3 gegnerische Räume mit einem einzigen Laserstrahl.",
        "category": "KAMPF",
    },
    {
        "id": "fire_starter",
        "title": "Pyromane",
        "desc": "Entfache in 3 Räumen des Gegners gleichzeitig Feuer.",
        "category": "KAMPF",
    },
    {
        "id": "crew_eliminator",
        "title": "Bio-Extinktion",
        "desc": "Eliminiere die gesamte gegnerische Crew ohne das Schiff zu zerstören.",
        "category": "KAMPF",
    },
    {
        "id": "bare_hull",
        "title": "Auf Messers Schneide",
        "desc": "Gewinne einen Kampf mit nur 1 HP verbleibender Hüllenenergie.",
        "category": "KAMPF",
    },
    {
        "id": "boarding_party",
        "title": "Entermannschaft",
        "desc": "Teleportiere eine Entermannschaft auf das gegnerische Schiff.",
        "category": "KAMPF",
    },

    # --- BESATZUNG & SKILLS ---
    {
        "id": "master_mechanic",
        "title": "Meister-Ingenieur",
        "desc": "Bringe den Reparatur-Skill eines Crew-Mitglieds auf Stufe 3.",
        "category": "CREW",
    },
    {
        "id": "master_warrior",
        "title": "Kriegsfürst",
        "desc": "Bringe den Nahkampf-Skill eines Crew-Mitglieds auf Stufe 3.",
        "category": "CREW",
    },
    {
        "id": "ace_pilot",
        "title": "As der Galaxie",
        "desc": "Bringe den Piloten-Skill eines Crew-Mitglieds auf Stufe 3.",
        "category": "CREW",
    },
    {
        "id": "full_house",
        "title": "Volles Haus",
        "desc": "Rekrutiere eine vollwertige Besatzung von 6 Crewmitgliedern.",
        "category": "CREW",
    },
    {
        "id": "alien_coalition",
        "title": "Galaktische Allianz",
        "desc": "Habe mindestens 4 verschiedene Spezies in deiner Crew.",
        "category": "CREW",
    },

    # --- SCHIFF & AUFRÜSTUNG ---
    {
        "id": "collector",
        "title": "Schiffs-Sammler",
        "desc": "Schalte mindestens 4 verschiedene Raumschiffe frei.",
        "category": "SCHIFF",
    },
    {
        "id": "armada",
        "title": "Sternen-Armada",
        "desc": "Schalte alle 8 Raumschiffe im Spiel frei!",
        "category": "SCHIFF",
    },
    {
        "id": "max_power",
        "title": "Maximale Reaktorleistung",
        "desc": "Rüste deinen Reaktor auf mindestens 25 Energiepunkte auf.",
        "category": "SCHIFF",
    },
    {
        "id": "impenetrable_shield",
        "title": "Unüberwindbare Barriere",
        "desc": "Besitze ein 4-schichtiges Schildsystem.",
        "category": "SCHIFF",
    },
    {
        "id": "weapon_fuser",
        "title": "Waffenschmied",
        "desc": "Führe eine erfolgreiche Waffen-Fusion im Shop durch.",
        "category": "SCHIFF",
    },

    # --- ERKUNDUNG & ÜBERLEBEN ---
    {
        "id": "survivor",
        "title": "Überlebenskünstler",
        "desc": "Triggere ein Event mit 0 Treibstoff und überlebe.",
        "category": "ERKUNDUNG",
    },
    {
        "id": "event_explorer",
        "title": "Weltraum-Erkunder",
        "desc": "Erfülle 10 zufällige Sektor-Events.",
        "category": "ERKUNDUNG",
    },
    {
        "id": "scrap_hoarder",
        "title": "Schrott-Millionär",
        "desc": "Besitze mindestens 250 Scrap auf einmal im Frachtraum.",
        "category": "ERKUNDUNG",
    },
    {
        "id": "nebula_ghost",
        "title": "Nebel-Phantom",
        "desc": "Durchquere mindestens 5 Nebel-Knoten in einem Spieldurchgang.",
        "category": "ERKUNDUNG",
    },
]


def format_german_datetime(ts_str: str | None) -> str:
    """Wandelt ein Datum/Zeit-String in das deutsche Format 'DD.MM.YYYY, HH:MM Uhr' um."""
    if not ts_str:
        return ""
    if "Uhr" in ts_str:
        return ts_str
    try:
        # ISO-Format YYYY-MM-DD HH:MM
        if "-" in ts_str and len(ts_str.split("-")[0]) == 4:
            clean = ts_str.replace("T", " ").strip()
            parts = clean.split(" ")
            ymd = parts[0].split("-")
            time_part = parts[1] if len(parts) > 1 else "00:00"
            return f"{ymd[2]}.{ymd[1]}.{ymd[0]}, {time_part[:5]} Uhr"
        # Punkt-Format DD.MM.YYYY HH:MM
        if "." in ts_str:
            clean = ts_str.strip()
            parts = clean.split(" ")
            dmy = parts[0]
            time_part = parts[1] if len(parts) > 1 else "00:00"
            return f"{dmy}, {time_part[:5]} Uhr"
    except Exception:
        pass
    return f"{ts_str} Uhr"


class AchievementManager:

    def __init__(self, filepath: str = ACHIEVEMENT_FILE):
        self.filepath = filepath
        self.achievements: dict[str, dict[str, str | list[str] | bool | float | str | None]] = {}
        self.toasts: list[dict[str, Any]] = []  # Active popups
        self.game: "Game | None" = None   # Set by Game after construction
        self.sound: SoundManager | None = None   # Set by Game after construction
        self.init_achievements()
        self.load_achievements()

    def init_achievements(self):
        for item in ACHIEVEMENTS_MASTER:
            a_id = item["id"]
            self.achievements[a_id] = {
                "id": a_id,
                "title": item["title"],
                "desc": item["desc"],
                "category": item.get("category", "KAMPF"),
                "unlocked": False,
                "unlock_time": None,
            }

    def unlock(self, a_id: str) -> bool:
        if a_id in self.achievements and not self.achievements[a_id]["unlocked"]:
            self.achievements[a_id]["unlocked"] = True
            self.achievements[a_id]["unlock_time"] = time.strftime("%d.%m.%Y, %H:%M Uhr")
            self.save_achievements()

            # Push toast notification
            self.toasts.append(
                {
                    "title": self.achievements[a_id]["title"],
                    "desc": self.achievements[a_id]["desc"],
                    "timer": 4.0,  # 4 seconds display
                }
            )
            snd = getattr(self, "sound", None)
            if snd:
                snd.play("achievement")
            return True
        return False

    def load_achievements(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)
                    for a_id, item in saved_data.items():
                        if a_id in self.achievements:
                            self.achievements[a_id]["unlocked"] = item.get("unlocked", False)
                            self.achievements[a_id]["unlock_time"] = item.get("unlock_time")
            except Exception as e:
                print(f"Fehler beim Laden von {self.filepath}: {e}")

    def save_achievements(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.achievements, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern von {self.filepath}: {e}")

    def update_toasts(self, dt: float):
        for toast in self.toasts[:]:
            current = float(toast["timer"])
            toast["timer"] = current - dt
            if toast["timer"] <= 0:
                self.toasts.remove(toast)

    def draw_toasts(self, surface: pygame.Surface, font: pygame.font.Font):
        if not self.toasts:
            return

        toast = self.toasts[0]  # Display topmost active toast
        w, h = 420, 60
        x = (surface.get_width() - w) // 2
        y = 15

        # Banner Surface
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((15, 35, 60, 235))
        surface.blit(surf, (x, y))

        pygame.draw.rect(surface, (255, 215, 0), (x, y, w, h), 2)
        pygame.draw.rect(surface, (255, 180, 0), (x + 2, y + 2, w - 4, h - 4), 1)

        header = font.render(f"ERRUNGENSCHAFT: {toast['title']}", True, (255, 230, 100))
        surface.blit(header, (x + 15, y + 8))

        sub_font = pygame.font.SysFont(None, 18)
        desc_txt = sub_font.render(toast["desc"], True, (220, 235, 255))
        surface.blit(desc_txt, (x + 15, y + 34))
