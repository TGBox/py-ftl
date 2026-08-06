
# Farben
COLOR_BG = (15, 18, 24)
COLOR_ROOM = (40, 50, 70)
COLOR_ENEMY_ROOM = (70, 40, 50)
COLOR_BORDER = (100, 140, 180)
COLOR_ENEMY_BORDER = (180, 100, 100)
COLOR_CREW = (50, 200, 100)
COLOR_SELECTED = (255, 200, 0)
COLOR_POWER_ACTIVE = (0, 220, 120)
COLOR_POWER_OFF = (60, 70, 80)
COLOR_REACTOR = (0, 180, 255)
COLOR_WEAPON_CHARGE = (255, 180, 0)
COLOR_PROJECTILE = (255, 50, 50)
COLOR_MAP_NODE = (150, 180, 220)
COLOR_MAP_VISITED = (75, 95, 115)
COLOR_MAP_LINE = (50, 70, 100)
COLOR_SHOP_NODE = (220, 180, 60)
COLOR_TRAINING_NODE = (180, 100, 220)
COLOR_HP_GREEN = (50, 220, 100)
COLOR_HP_RED = (220, 60, 60)

# Zielschusslinien-Farben für verschiedene Waffen
WEAPON_LINE_COLORS = [
    (255, 80, 80),   # Waffe 1: Hellrot
    (80, 220, 255),  # Waffe 2: Cyan
    (255, 200, 50),  # Waffe 3: Gelb
    (220, 100, 255), # Waffe 4: Violett
    (100, 255, 150), # Waffe 5: Grün
]

# Zustände
STATE_MAP = "MAP"
STATE_EVENT = "EVENT"
STATE_COMBAT = "COMBAT"
STATE_SHOP = "SHOP"
STATE_TRAINING = "TRAINING"
STATE_GAME_OVER = "GAME_OVER"
STATE_VICTORY = "VICTORY"
STATE_MAIN_MENU = "MAIN_MENU"
STATE_OPTIONS = "OPTIONS"
current_state: str = STATE_MAP

# Logische Spielauflösung (intern immer 900x600 gerendert, dann skaliert).
LOGICAL_WIDTH = 900
LOGICAL_HEIGHT = 600

# Verfügbare Fensterauflösungen (inkl. Ultrawide)
RESOLUTIONS = [
    (900, 600),
    (1280, 720),
    (1600, 900),
    (1920, 1080),
    (2560, 1080),   # Ultrawide 21:9
    (3440, 1440),   # Ultrawide 21:9 QHD
    (3840, 2160),   # 4K
]

# Generelle Größen.
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

# Rebellenflotte - Geschwindigkeit pro Sprung
REBEL_FLEET_SPEED = 55.0

# Startkonfiguration.
PLAYER_START_FUEL = 6
PLAYER_START_SCRAP = 20
PLAYER_START_MISSILES = 6
PLAYER_START_POWER = 6
ENEMY_START_POWER = 6

# Font-Caching System (eliminiert CPU-Overhead durch SysFont Lookups)
import pygame
_FONT_CACHE: dict[tuple[int, bool], pygame.font.Font] = {}

def get_font(size: int = 18, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _FONT_CACHE:
        if not pygame.font.get_init():
            pygame.font.init()
        _FONT_CACHE[key] = pygame.font.SysFont(None, size, bold=bold)
    return _FONT_CACHE[key]