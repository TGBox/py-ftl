from typing import TYPE_CHECKING
    
import math
import struct
from typing import Callable
import pygame


if TYPE_CHECKING:
    from game import Game

class SoundManager:
    """Procedural sound effects & background music engine — generates all audio from synth waveforms."""

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
        self.game: Game | None = None   # Set by Game after construction

        self._generate_all()
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
                self._music_channel.stop()
                self._current_track_name = None
            return

        snd = self._music_tracks.get(track_name)
        if snd:
            if self._music_channel is None:
                self._music_channel = pygame.mixer.Channel(0)
            self._music_channel.stop()
            eff_vol = min(1.0, self._master_volume * self._music_volume)
            snd.set_volume(eff_vol)
            self._music_channel.set_volume(eff_vol)
            self._music_channel.play(snd, loops=-1)
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
    # Waveform & Synthesizer generation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_samples(
        duration_ms: int,
        freq: float,
        *,
        fade_out: bool = True,
        wave: str = "sin",
        sample_rate: int = 22050
    ) -> bytes:
        n_samples = int(sample_rate * duration_ms / 1000)
        samples: list[float] = []
        for i in range(n_samples):
            t = i / sample_rate
            if wave == "sin":
                val = math.sin(2 * math.pi * freq * t)
            elif wave == "square":
                val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            elif wave == "saw":
                val = 2.0 * (t * freq - math.floor(t * freq + 0.5))
            elif wave == "noise":
                import random
                val = random.uniform(-1, 1)
            else:
                val = math.sin(2 * math.pi * freq * t)

            if fade_out:
                envelope = max(0.0, 1.0 - i / n_samples)
                val *= envelope

            val = max(-1.0, min(1.0, val))
            samples.append(int(val * 32000))

        return struct.pack(f"<{len(samples)}h", *samples)

    @staticmethod
    def _make_sweep(
        duration_ms: int,
        start_freq: float,
        end_freq: float,
        *,
        wave: str = "square",
        sample_rate: int = 22050
    ) -> bytes:
        n_samples = int(sample_rate * duration_ms / 1000)
        samples: list[float] = []
        phase = 0.0
        for i in range(n_samples):
            t = i / n_samples
            cur_freq = start_freq + (end_freq - start_freq) * t
            phase += 2 * math.pi * cur_freq / sample_rate
            if wave == "sin":
                val = math.sin(phase)
            elif wave == "square":
                val = 1.0 if math.sin(phase) >= 0 else -1.0
            elif wave == "saw":
                val = 2.0 * ((phase / (2 * math.pi)) - math.floor((phase / (2 * math.pi)) + 0.5))
            else:
                val = math.sin(phase)

            envelope = max(0.0, 1.0 - t)
            val *= envelope
            val = max(-1.0, min(1.0, val))
            samples.append(int(val * 32000))

        return struct.pack(f"<{len(samples)}h", *samples)

    @staticmethod
    def _mix(buf_a: bytes, buf_b: bytes) -> bytes:
        """Mix two equal-length 16-bit signed buffers."""
        n = min(len(buf_a), len(buf_b)) // 2
        a = struct.unpack(f"<{n}h", buf_a[:n * 2])
        b = struct.unpack(f"<{n}h", buf_b[:n * 2])
        mixed = [max(-32000, min(32000, (x + y) // 2)) for x, y in zip(a, b)]
        return struct.pack(f"<{len(mixed)}h", *mixed)

    def _sound(self, data: bytes) -> pygame.mixer.Sound:
        return pygame.mixer.Sound(buffer=data)

    # ------------------------------------------------------------------
    # Generate all game sound effects
    # ------------------------------------------------------------------

    def _generate_all(self) -> None:
        # --- Laser fire ---
        self._cache["laser_fire"] = self._sound(self._make_samples(180, 880, wave="square"))

        # --- Missile fire ---
        self._cache["missile_fire"] = self._sound(self._make_samples(300, 220, wave="saw"))

        # --- Beam fire ---
        self._cache["beam_fire"] = self._sound(self._make_samples(400, 600, wave="sin"))

        # --- Flak fire ---
        raw_flak = self._make_samples(200, 150, wave="noise", fade_out=True)
        self._cache["flak_fire"] = self._sound(raw_flak)

        # --- Ion fire & Hit ---
        self._cache["ion_fire"] = self._sound(self._make_sweep(220, 1400, 300, wave="square"))
        raw_ion_hit = self._mix(
            self._make_samples(180, 800, wave="square", fade_out=True),
            self._make_samples(180, 300, wave="noise", fade_out=True)
        )
        self._cache["ion_hit"] = self._sound(raw_ion_hit)

        # --- Teleport & Cloak ---
        self._cache["teleport"] = self._sound(self._make_sweep(280, 200, 1200, wave="sin"))
        self._cache["cloak"] = self._sound(self._make_sweep(350, 900, 180, wave="sin"))

        # --- Shield & Hull ---
        self._cache["shield_hit"] = self._sound(self._make_samples(120, 1200, wave="sin"))
        self._cache["shield_recharge"] = self._sound(self._make_sweep(200, 200, 600, wave="sin"))
        raw_hit = self._make_samples(160, 100, wave="noise", fade_out=True)
        self._cache["hull_hit"] = self._sound(raw_hit)

        # --- Explosion (enemy destroyed) ---
        raw_exp = self._make_samples(500, 60, wave="noise", fade_out=True)
        self._cache["explosion"] = self._sound(raw_exp)

        # --- Button click & Purchase ---
        self._cache["click"] = self._sound(self._make_samples(50, 1400, wave="sin"))
        self._cache["purchase"] = self._sound(self._make_samples(200, 660, wave="sin"))

        # --- Jump / travel ---
        self._cache["jump"] = self._sound(self._make_samples(350, 440, wave="sin", fade_out=True))

        # --- Warning / alarm / Low Fuel ---
        raw_a = self._make_samples(300, 500, wave="square", fade_out=False)
        raw_b = self._make_samples(300, 400, wave="square", fade_out=False)
        self._cache["alarm"] = self._sound(raw_a + raw_b)
        self._cache["low_fuel"] = self._sound(self._make_samples(350, 350, wave="saw", fade_out=True))

        # --- Crew death & Repair ---
        self._cache["crew_death"] = self._sound(self._make_samples(250, 200, wave="saw", fade_out=True))
        self._cache["repair"] = self._sound(self._make_samples(150, 1000, wave="sin"))
        self._cache["door"] = self._sound(self._make_samples(80, 300, wave="square"))

        # --- Achievement Fanfare ---
        ach_notes = [523, 659, 784, 988, 1047]  # C5-E5-G5-B5-C6
        ach_buf = b""
        for freq in ach_notes:
            ach_buf += self._make_samples(120, freq, wave="sin", fade_out=True)
        self._cache["achievement"] = self._sound(ach_buf)

        # --- Victory & Game Over ---
        notes = [523, 659, 784, 1047]
        fanfare = b""
        for freq in notes:
            fanfare += self._make_samples(200, freq, wave="sin", fade_out=False)
        self._cache["victory"] = self._sound(fanfare)

        go = self._make_samples(600, 150, wave="saw", fade_out=True)
        self._cache["game_over"] = self._sound(go)

    # ------------------------------------------------------------------
    # Generate procedural background music loops (Synth BGM)
    # ------------------------------------------------------------------

    def _generate_music(self) -> None:
        """Loads custom music files from assets/music/ or falls back to procedural tracks."""
        import os
        sample_rate = 22050

        music_dir = "assets/music"
        os.makedirs(music_dir, exist_ok=True)

        expected_tracks = ["bgm_menu", "bgm_explore", "bgm_combat", "bgm_boss"]
        loaded_from_file: set[str] = set()

        for track in expected_tracks:
            for ext in [".ogg", ".wav", ".mp3"]:
                filepath = os.path.join(music_dir, f"{track}{ext}")
                if os.path.exists(filepath):
                    try:
                        self._music_tracks[track] = pygame.mixer.Sound(filepath)
                        loaded_from_file.add(track)
                        print(f"Musik erfolgreich geladen aus {filepath}")
                        break
                    except Exception as e:
                        print(f"Fehler beim Laden von {filepath}: {e}")

        # procedural fallbacks for any missing tracks
        if len(loaded_from_file) == len(expected_tracks):
            return

        # Helper functions for Orchestral Voice Synthesis
        def string_section(t: float, freqs: list[float], vol: float = 1.0) -> float:
            """Multi-voice detuned string ensemble with harmonics, LFO vibrato & lowpass warmth."""
            if not freqs:
                return 0.0
            vibrato = 1.0 + 0.0025 * math.sin(2 * math.pi * 4.8 * t)
            total = 0.0
            detunes = [1.0, 1.002, 0.998]
            for f in freqs:
                if f <= 0:
                    continue
                for d in detunes:
                    eff_f = f * vibrato * d
                    v = (
                        math.sin(2 * math.pi * eff_f * t) * 0.55 +
                        math.sin(2 * math.pi * eff_f * 2.0 * t) * 0.28 +
                        math.sin(2 * math.pi * eff_f * 3.0 * t) * 0.12 +
                        math.sin(2 * math.pi * eff_f * 4.0 * t) * 0.05
                    )
                    total += v
            return (total / (len(freqs) * len(detunes))) * vol

        def french_horn_chord(t: float, freqs: list[float], vol: float = 1.0) -> float:
            """Warm, noble brass chord with rich fundamental and even harmonics."""
            if not freqs:
                return 0.0
            vibrato = 1.0 + 0.0015 * math.sin(2 * math.pi * 4.2 * t)
            total = 0.0
            for f in freqs:
                if f <= 0:
                    continue
                eff_f = f * vibrato
                v = (
                    math.sin(2 * math.pi * eff_f * t) * 0.50 +
                    math.sin(2 * math.pi * eff_f * 2.0 * t) * 0.35 +
                    math.sin(2 * math.pi * eff_f * 3.0 * t) * 0.10 +
                    math.sin(2 * math.pi * eff_f * 4.0 * t) * 0.05
                )
                total += v
            return (total / len(freqs)) * vol

        def harp_pizz(t_rel: float, freq: float, vol: float = 1.0) -> float:
            """Plucked string / harp note with instant attack and natural exponential decay."""
            if t_rel < 0 or freq <= 0:
                return 0.0
            decay = math.exp(-6.5 * t_rel)
            if decay < 0.001:
                return 0.0
            val = math.sin(2 * math.pi * freq * t_rel) * 0.7 + math.sin(2 * math.pi * freq * 2.0 * t_rel) * 0.3
            return val * decay * vol

        def timpani_hit(t_rel: float, base_freq: float = 85.0, vol: float = 1.0) -> float:
            """Low resonant orchestral timpani drum hit."""
            if t_rel < 0 or t_rel > 1.2:
                return 0.0
            decay = math.exp(-4.0 * t_rel)
            pitch = base_freq * (1.0 + 0.35 * math.exp(-14.0 * t_rel))
            val = math.sin(2 * math.pi * pitch * t_rel) * decay
            return val * vol

        def build_orchestral_buffer(duration_sec: float, generator_fn: Callable[[float], float], alpha_lpf: float = 0.30) -> bytes:
            n_samples = int(sample_rate * duration_sec)
            raw: list[float] = []
            for i in range(n_samples):
                t = i / sample_rate
                raw.append(generator_fn(t))

            # Warm low-pass filter to eliminate digital harshness
            smooth = 0.0
            pcm: list[float] = []
            for v in raw:
                smooth += alpha_lpf * (v - smooth)
                pcm.append(int(max(-1.0, min(1.0, smooth)) * 26000))

            return struct.pack(f"<{len(pcm)}h", *pcm)

        # 1. BGM Menu: Orchestral Space Prelude (12.0s loop) - Gentle & Warm
        if "bgm_menu" not in loaded_from_file:
            def menu_synth(t: float) -> float:
                chord_idx = int(t / 3.0) % 4
                chords_strings = [
                    [130.81, 196.00, 246.94, 329.63, 392.00],  # C3, G3, B3, E4, G4 (Cmaj9)
                    [110.00, 164.81, 196.00, 261.63, 329.63],  # A2, E3, G3, C4, E4 (Am9)
                    [87.31,  130.81, 164.81, 220.00, 261.63],  # F2, C3, E3, A3, C4 (Fmaj7)
                    [98.00,  146.83, 185.00, 246.94, 293.66],  # G2, D3, F#3, B3, D4 (G6)
                ]
                chords_horns = [
                    [65.41, 130.81],  # C2, C3
                    [55.00, 110.00],  # A1, A2
                    [43.65, 87.31],   # F1, F2
                    [49.00, 98.00],   # G1, G2
                ]

                t_chord = (t % 3.0)
                crescendo = min(1.0, t_chord / 0.6) * max(0.0, 1.0 - max(0.0, t_chord - 2.4) / 0.6)

                s_val = string_section(t, chords_strings[chord_idx], vol=0.55 * crescendo)
                h_val = french_horn_chord(t, chords_horns[chord_idx], vol=0.35 * crescendo)

                harp_notes = [523.25, 659.25, 783.99, 987.77, 1046.50]
                t_harp = (t % 0.75)
                harp_idx = int(t / 0.75) % len(harp_notes)
                hp_val = harp_pizz(t_harp, harp_notes[harp_idx], vol=0.25)

                return s_val + h_val + hp_val

            self._music_tracks["bgm_menu"] = self._sound(build_orchestral_buffer(12.0, menu_synth, alpha_lpf=0.28))

        # 2. BGM Explore: Galactic Symphony (16.0s loop) - Evolving & Beautiful
        if "bgm_explore" not in loaded_from_file:
            def exp_synth(t: float) -> float:
                m_idx = int(t / 4.0) % 4
                str_chords = [
                    [110.0, 164.81, 220.0, 261.63, 329.63], # Am
                    [87.31, 130.81, 174.61, 220.0, 261.63], # F
                    [130.81, 164.81, 196.0, 261.63, 392.0], # C
                    [98.0, 146.83, 196.0, 246.94, 293.66],  # G
                ]
                t_m = t % 4.0
                env = min(1.0, t_m / 0.7) * max(0.0, 1.0 - max(0.0, t_m - 3.3) / 0.7)

                s_val = string_section(t, str_chords[m_idx], vol=0.55 * env)

                harp_seq = [220.0, 261.63, 329.63, 392.0, 440.0, 523.25, 659.25, 783.99]
                t_h = t % 0.5
                h_idx = int(t / 0.5) % len(harp_seq)
                hp_val = harp_pizz(t_h, harp_seq[h_idx], vol=0.30)

                t_timp = timpani_hit(t_m, base_freq=75.0, vol=0.40)

                return s_val + hp_val + t_timp

            self._music_tracks["bgm_explore"] = self._sound(build_orchestral_buffer(16.0, exp_synth, alpha_lpf=0.30))

        # 3. BGM Combat: Heroic Battle Symphony (12.8s loop) - Dynamic & Epic
        if "bgm_combat" not in loaded_from_file:
            def combat_synth(t: float) -> float:
                ost_freqs = [146.83, 220.00, 293.66, 349.23, 293.66, 220.00, 146.83, 174.61]
                t_ost = t % 0.2
                ost_idx = int(t / 0.2) % len(ost_freqs)
                f_ost = ost_freqs[ost_idx]
                ost_env = math.exp(-8.0 * t_ost)
                ost_val = string_section(t, [f_ost], vol=0.45 * ost_env)

                horn_chords = [
                    [73.42, 146.83, 220.00],   # Dm
                    [87.31, 174.61, 261.63],   # F
                    [98.00, 196.00, 246.94],   # G
                    [65.41, 130.81, 196.00],   # C
                ]
                h_idx = int(t / 1.6) % 4
                t_h = t % 1.6
                h_env = min(1.0, t_h / 0.3) * max(0.0, 1.0 - max(0.0, t_h - 1.3) / 0.3)
                horn_val = french_horn_chord(t, horn_chords[h_idx], vol=0.50 * h_env)

                timp_val = timpani_hit(t_h, base_freq=80.0, vol=0.60)

                return ost_val + horn_val + timp_val

            self._music_tracks["bgm_combat"] = self._sound(build_orchestral_buffer(12.8, combat_synth, alpha_lpf=0.32))

        # 4. BGM Boss: Grand Flagship Overture (12.8s loop) - Dramatic & Powerful
        if "bgm_boss" not in loaded_from_file:
            def boss_synth(t: float) -> float:
                _ = t % 0.15
                tr_freqs = [65.41, 98.00, 130.81, 155.56]  # C2, G2, C3, Eb3
                tr_idx = int(t / 0.15) % len(tr_freqs)
                cell_val = string_section(t, [tr_freqs[tr_idx]], vol=0.50)

                brass_chords = [
                    [65.41, 130.81, 196.00, 233.08],  # Cm7
                    [58.27, 116.54, 174.61, 233.08],  # Bb
                    [43.65, 87.31, 130.81, 174.61],   # Fm
                    [49.00, 98.00, 146.83, 196.00],   # G
                ]
                b_idx = int(t / 1.6) % 4
                t_b = t % 1.6
                b_env = min(1.0, t_b / 0.25) * max(0.0, 1.0 - max(0.0, t_b - 1.35) / 0.25)
                brass_val = french_horn_chord(t, brass_chords[b_idx], vol=0.60 * b_env)

                timp_val = timpani_hit(t_b, base_freq=65.0, vol=0.75)

                return cell_val + brass_val + timp_val

            self._music_tracks["bgm_boss"] = self._sound(build_orchestral_buffer(12.8, boss_synth, alpha_lpf=0.32))
