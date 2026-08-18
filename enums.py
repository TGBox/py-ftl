from enum import Enum

class GameState(str, Enum):
    MAIN_MENU = "MAIN_MENU"
    MAP = "MAP"
    EVENT = "EVENT"
    COMBAT = "COMBAT"
    SHOP = "SHOP"
    TRAINING = "TRAINING"
    GAME_OVER = "GAME_OVER"
    VICTORY = "VICTORY"
    OPTIONS = "OPTIONS"
    ACHIEVEMENTS = "ACHIEVEMENTS"
