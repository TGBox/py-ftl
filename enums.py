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


class HazardType(str, Enum):
    NONE = "NONE"
    SOLAR_FLARE = "SOLAR_FLARE"
    ASTEROID_FIELD = "ASTEROID_FIELD"
    PULSAR = "PULSAR"
    ION_STORM = "ION_STORM"


class WeaponType(str, Enum):
    LASER = "LASER"
    MISSILE = "MISSILE"
    BEAM = "BEAM"
    ION = "ION"
    BOMB = "BOMB"
    FLAK = "FLAK"


class WeaponSubtype(str, Enum):
    STANDARD = "STANDARD"
    BIO = "BIO"
    FIRE = "FIRE"
    BREACH = "BREACH"
    STUN = "STUN"
    HEAVY = "HEAVY"


class SystemType(str, Enum):
    SHIELD = "Schild"
    WEAPONS = "Waffen"
    BRIDGE = "Brücke"
    ENGINES = "Maschinen"
    MEDBAY = "Medbay"
    TELEPORTER = "Teleporter"
    CLOAKING = "Tarnung"
    DRONE_CONTROL = "Drohnen-Kontrolle"
    SENSORS = "Sensoren"
    REACTOR = "Reaktor"
    OXYGEN = "Sauerstoff"
    DOORS = "Türen"

