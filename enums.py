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


class EventType(str, Enum):
    COMBAT = "COMBAT"
    RESOURCE = "RESOURCE"
    DISTRESS = "DISTRESS"
    NEBULA = "NEBULA"
    SHOP = "SHOP"
    TRAINING = "TRAINING"
    EMPTY = "EMPTY"
    BOSS = "BOSS"


class CrewSpecies(str, Enum):
    MENSCH = "Mensch"
    ENGI = "Engi"
    MANTIS = "Mantis"
    ROCK = "Rock"
    ZOLTAN = "Zoltan"


class CrewTrait(str, Enum):
    ALLROUNDER = "Allrounder"
    REPARATUR_GENIE = "Reparatur-Genie"
    NAHKAMPF_EXPERTE = "Nahkampf-Experte"
    PANZERUNG = "Panzerung"
    ENERGIEGEBER = "Energiegeber"


class DroneType(str, Enum):
    COMBAT_MK1 = "COMBAT_MK1"
    REPAIR = "REPAIR"
    DEFENSE_MK1 = "DEFENSE_MK1"
    SHIELD_CHARGER = "SHIELD_CHARGER"
    ANTI_PERSONNEL = "ANTI_PERSONNEL"


class ShipType(str, Enum):
    KESTREL = "Kestrel"
    TARNSSCHIFF = "Tarnschiff"
    FEDERATION_CRUISER = "Federation Cruiser"
    MANTIS_CRUISER = "Mantis Cruiser"
    ROCK_CRUISER = "Rock Cruiser"
    ZOLTAN_CRUISER = "Zoltan Cruiser"
    ENGI_CRUISER = "Engi Cruiser"
    SLUG_CRUISER = "Slug Cruiser"
    REBEL_SCOUT = "Rebellen-Späher"
    REBEL_FIGHTER = "Rebellen-Jäger"
    REBEL_FLAGSHIP = "Rebellen-Flaggschiff"
