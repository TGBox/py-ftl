import os
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from game import Game

class SoundManager:
    """Audio engine for SFX and background music playback."""

    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self._cache: dict[str, pygame.mixer.Sound] = {}
        self._music_tracks: dict[str, pygame.mixer.Sound] = {}
        self._enabled: bool = True
        self._music_enabled: bool = True
        self._master_volume: float = 1.0
        self._music_volume: float = 1.0
        self._sfx_volume: float = 0.25
        self._current_track_name: str | None = None
        self._music_channel: pygame.mixer.Channel | None = None
        self.game: "Game | None" = None

        self._load_all()
        self._generate_music()

    # ------------------------------------------------------------------
    # Public API - SFX & Music
    # ------------------------------------------------------------------

    def _update_music_volume(self) -> None:
        if self._music_channel and self._current_track_name:
            snd = self._music_tracks.get(self._current_track_name)
            eff_vol = min(1.0, self._master_volume * self._music_volume) if self._music_enabled else 0.0
            if snd:
                snd.set_volume(eff_vol)
            self._music_channel.set_volume(eff_vol)

    def play(self, name: str) -> None:
        if not self._enabled:
            return
        snd = self._cache.get(name)
        if snd:
            eff_vol = min(1.0, self._master_volume * self._sfx_volume)
            snd.set_volume(eff_vol)
            snd.play()

    def play_music(self, track_name: str) -> None:
        if not self._music_enabled or self._current_track_name == track_name:
            if not self._music_enabled and self._music_channel:
                self._music_channel.fadeout(300)
                self._current_track_name = None
            return

        snd = self._music_tracks.get(track_name)
        if snd:
            if self._music_channel is None:
                self._music_channel = pygame.mixer.Channel(0)
            else:
                self._music_channel.fadeout(300)
            eff_vol = min(1.0, self._master_volume * self._music_volume)
            snd.set_volume(eff_vol)
            self._music_channel.set_volume(eff_vol)
            self._music_channel.play(snd, loops=-1, fade_ms=400)
            self._current_track_name = track_name

    def stop_music(self) -> None:
        if self._music_channel:
            self._music_channel.stop()
        self._current_track_name = None

    def toggle(self) -> bool:
        self._enabled = not self._enabled
        self._music_enabled = self._enabled
        if not self._music_enabled:
            self.stop_music()
        else:
            self._update_music_volume()
        return self._enabled

    def toggle_music(self) -> bool:
        self._music_enabled = not self._music_enabled
        if not self._music_enabled:
            self.stop_music()
        else:
            self._update_music_volume()
        return self._music_enabled

    @property
    def master_volume(self) -> float:
        return self._master_volume

    @master_volume.setter
    def master_volume(self, val: float) -> None:
        self._master_volume = max(0.0, min(2.0, val))
        self._update_music_volume()

    @property
    def music_volume(self) -> float:
        return self._music_volume

    @music_volume.setter
    def music_volume(self, val: float) -> None:
        self._music_volume = max(0.0, min(2.0, val))
        self._update_music_volume()

    @property
    def sfx_volume(self) -> float:
        return self._sfx_volume

    @sfx_volume.setter
    def sfx_volume(self, val: float) -> None:
        self._sfx_volume = max(0.0, min(2.0, val))

    @property
    def volume(self) -> float:
        return self._sfx_volume

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def music_enabled(self) -> bool:
        return self._music_enabled

    # ------------------------------------------------------------------
    # Load all game sound effects
    # ------------------------------------------------------------------

    def _load_all(self) -> None:
        sound_names = [
            "laser_fire", "missile_fire", "beam_fire", "flak_fire", "ion_fire", "ion_hit",
            "teleport", "cloak", "shield_hit", "shield_recharge", "hull_hit", "explosion",
            "click", "purchase", "jump", "alarm", "low_fuel", "crew_death", "repair",
            "door", "achievement", "victory", "game_over",
        ]
        dummy_sound = None
        for name in sound_names:
            path = f"assets/sounds/{name}.wav"
            try:
                self._cache[name] = pygame.mixer.Sound(path)
            except Exception:
                if dummy_sound is None:
                    dummy_sound = pygame.mixer.Sound(buffer=b"\x00" * 44)
                self._cache[name] = dummy_sound

    # ------------------------------------------------------------------
    # Load background music tracks
    # ------------------------------------------------------------------

    def _generate_music(self) -> None:
        """Loads music files from assets/music/."""
        music_dir = "assets/music"
        expected_tracks = ["bgm_menu", "bgm_explore", "bgm_combat", "bgm_boss", "bgm_civilian", "bgm_nebula", "bgm_pirate"]

        for track in expected_tracks:
            for ext in [".ogg", ".wav", ".mp3"]:
                filepath = os.path.join(music_dir, f"{track}{ext}")
                if os.path.exists(filepath):
                    try:
                        self._music_tracks[track] = pygame.mixer.Sound(filepath)
                        break
                    except Exception:
                        pass
            if track not in self._music_tracks:
                self._music_tracks[track] = pygame.mixer.Sound(buffer=b"\x00" * 44)
