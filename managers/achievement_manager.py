import json
import os
import time
import pygame

ACHIEVEMENT_FILE = "data/achievements.json"

ACHIEVEMENTS_MASTER = [
    {
        "id": "first_victory",
        "title": "Erster Sieg",
        "desc": "Besiege ein feindliches Raumschiff im Gefecht.",
        "icon": "⚔️",
    },
    {
        "id": "boss_slayer",
        "title": "Rebellen-Schreck",
        "desc": "Besiege einen Sektor Mini-Boss.",
        "icon": "💥",
    },
    {
        "id": "flagship_down",
        "title": "Galaktischer Retter",
        "desc": "Zerstöre das Endboss-Flaggschiff der Rebellen!",
        "icon": "🏆",
    },
    {
        "id": "master_mechanic",
        "title": "Meister-Ingenieur",
        "desc": "Bringe den Reparatur-Skill eines Crew-Mitglieds auf Stufe 3.",
        "icon": "🔧",
    },
    {
        "id": "master_warrior",
        "title": "Kriegsfürst",
        "desc": "Bringe den Nahkampf-Skill eines Crew-Mitglieds auf Stufe 3.",
        "icon": "⚔️",
    },
    {
        "id": "collector",
        "title": "Schiffs-Sammler",
        "desc": "Schalte mindestens 4 verschiedene Raumschiffe frei.",
        "icon": "🚀",
    },
    {
        "id": "survivor",
        "title": "Überlebenskünstler",
        "desc": "Triggere ein Event mit 0 Treibstoff und überlebe.",
        "icon": "⚓",
    },
    {
        "id": "full_house",
        "title": "Volles Haus",
        "desc": "Rekrutiere eine vollwertige Besatzung von 6 Crewmitgliedern.",
        "icon": "👥",
    },
    {
        "id": "weapon_fuser",
        "title": "Waffenschmied",
        "desc": "Führe eine erfolgreiche Waffen-Fusion im Shop durch.",
        "icon": "⚡",
    },
    {
        "id": "event_explorer",
        "title": "Weltraum-Erkunder",
        "desc": "Erfülle 10 zufällige Sektor-Events.",
        "icon": "🌌",
    },
]


class AchievementManager:

    def __init__(self, filepath: str = ACHIEVEMENT_FILE):
        self.filepath = filepath
        self.achievements: dict[str, dict] = {}
        self.toasts: list[dict] = []  # Active popups
        self.init_achievements()
        self.load_achievements()

    def init_achievements(self):
        for item in ACHIEVEMENTS_MASTER:
            a_id = item["id"]
            self.achievements[a_id] = {
                "id": a_id,
                "title": item["title"],
                "desc": item["desc"],
                "icon": item["icon"],
                "unlocked": False,
                "unlock_time": None,
            }

    def unlock(self, a_id: str) -> bool:
        if a_id in self.achievements and not self.achievements[a_id]["unlocked"]:
            self.achievements[a_id]["unlocked"] = True
            self.achievements[a_id]["unlock_time"] = time.strftime("%Y-%m-%d %H:%M")
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
            toast["timer"] -= dt
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

        header = font.render(f"🏆 ERRUNGENSCHAFT: {toast['title']}", True, (255, 230, 100))
        surface.blit(header, (x + 15, y + 8))

        sub_font = pygame.font.SysFont(None, 18)
        desc_txt = sub_font.render(toast["desc"], True, (220, 235, 255))
        surface.blit(desc_txt, (x + 15, y + 34))
