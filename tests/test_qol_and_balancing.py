import pytest
import pygame
from classes.GameData import GameData
from classes.ShipModel import (
    ENEMY_SCOUT, REBEL_PURSUER_S1, REBEL_PURSUER_S2,
    REBEL_PURSUER_S3, REBEL_PURSUER_S4, REBEL_PURSUER_S5
)
from classes.Crew import Crew
from classes.Room import Room
from classes.Door import Door
from managers.combat_manager import CombatManager
from managers.map_manager import MapManager
from managers.sound_manager import SoundManager
from settings import GameState


@pytest.fixture
def test_env():
    pygame.init()
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    data = GameData()
    sound = SoundManager()
    combat = CombatManager(data)
    combat.sound = sound
    map_mgr = MapManager(data)
    return data, combat, map_mgr, sound


def test_quick_door_controls(test_env):
    data, combat, _, _ = test_env
    r1 = Room("Brücke", (100, 100, 80, 80))
    r2 = Room("Antrieb", (200, 100, 80, 80))
    data.player.ship.rooms = [r1, r2]

    # Create internal doors and one airlock
    d1 = Door(r1, r2, (180, 130, 20, 20), is_airlock=False)
    d2 = Door(r2, None, (280, 130, 20, 20), is_airlock=False)
    d_air = Door(r1, None, (100, 90, 20, 20), is_airlock=True)
    data.player.ship.doors = [d1, d2, d_air]

    # Test open all internal doors
    combat.open_all_doors()
    assert d1.is_open is True
    assert d2.is_open is True
    assert d_air.is_open is False  # Airlock remains closed for safety

    # Test close all doors
    combat.close_all_doors()
    assert d1.is_open is False
    assert d2.is_open is False
    assert d_air.is_open is False


def test_crew_station_memory(test_env):
    data, combat, _, _ = test_env
    r_bridge = Room("Brücke", (100, 100, 80, 80))
    r_engines = Room("Antrieb", (200, 100, 80, 80))
    data.player.ship.rooms = [r_bridge, r_engines]

    c1 = Crew(140, 140, name="Alice")
    c1.current_room = r_bridge
    c2 = Crew(240, 140, name="Bob")
    c2.current_room = r_engines
    data.player.crew = [c1, c2]

    # Save stations
    combat.save_crew_stations()
    assert "Alice" in combat.saved_crew_stations
    assert "Bob" in combat.saved_crew_stations
    assert combat.saved_crew_stations["Alice"][:2] == (140.0, 140.0)

    # Move crew elsewhere
    c1.x, c1.y = 50.0, 50.0
    c2.x, c2.y = 60.0, 60.0

    # Recall to stations
    combat.return_crew_to_stations()
    assert c1.target_pos == (140, 140)
    assert c2.target_pos == (240, 140)


def test_dynamic_rebel_pursuer_scaling(test_env):
    data, _, map_mgr, _ = test_env

    # Sector 1
    data.world.star_map.sector = 1
    map_mgr.start_rebel_pursuit_combat()
    assert data.enemy.ship.name == "Rebellen-Aufklärer (S1)"
    assert data.enemy.ship.max_hp == 10
    assert data.enemy.shield.max_layers == 1

    # Sector 3
    data.world.star_map.sector = 3
    map_mgr.start_rebel_pursuit_combat()
    assert data.enemy.ship.name == "Rebellen-Bomber (S3)"
    assert data.enemy.ship.max_hp == 18
    assert data.enemy.shield.max_layers == 2

    # Sector 5
    data.world.star_map.sector = 5
    map_mgr.start_rebel_pursuit_combat()
    assert data.enemy.ship.name == "Flotten-Elite-Kreuzer (S5)"
    assert data.enemy.ship.max_hp == 28
    assert data.enemy.shield.max_layers == 3


def test_boss_surge_timer_and_prewarning(test_env):
    data, combat, _, _ = test_env
    data.current_state = GameState.COMBAT
    data.enemy.ship.name = "Flaggschiff"
    data.combat.boss_phase = 2
    data.combat.drone_surge_timer = 2.0
    combat.surge_warned = False

    # Advance time by 0.6s -> timer reaches 1.4s (triggers surge warning)
    combat.update(0.6)
    assert combat.surge_warned is True
    assert data.combat.drone_surge_timer == pytest.approx(1.4, 0.05)


def test_sound_manager_crossfade(test_env):
    _, _, _, sound = test_env
    # Ensure play_music doesn't crash with 400ms crossfade
    sound.play_music("bgm_explore")
    assert sound._current_track_name == "bgm_explore"
    sound.play_music("bgm_combat")
    assert sound._current_track_name == "bgm_combat"
