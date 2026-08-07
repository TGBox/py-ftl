import math
import struct
import pygame


class SoundManager:
    """Procedural sound effects & background music engine — generates all audio from synth waveforms."""

    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self._cache: dict[str, pygame.mixer.Sound] = {}
        self._music_tracks: dict[str, pygame.mixer.Sound] = {}
        self._enabled: bool = True
        self._music_enabled: bool = True
        self._volume: float = 0.5
        self._music_volume: float = 0.35
        self._current_track_name: str | None = None
        self._music_channel: pygame.mixer.Channel | None = None

        self._generate_all()
        self._generate_music()

    # ------------------------------------------------------------------
    # Public API - SFX & Music
    # ------------------------------------------------------------------

    def play(self, name: str) -> None:
        if not self._enabled:
            return
        snd = self._cache.get(name)
        if snd:
            snd.set_volume(self._volume)
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
                self._music_channel = pygame.mixer.Channel(7)
            self._music_channel.stop()
            self._music_channel.set_volume(self._music_volume)
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
        return self._enabled

    def toggle_music(self) -> bool:
        self._music_enabled = not self._music_enabled
        if not self._music_enabled:
            self.stop_music()
        return self._music_enabled

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
        samples = []
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
        samples = []
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
        """Procedurally generate ambient synth BGM tracks."""
        sample_rate = 22050

        # Track 1: bgm_menu (Atmospheric Space Pad - 4.0s loop)
        menu_pad = b""
        menu_freqs = [261.63, 329.63, 392.00, 493.88]  # C4, E4, G4, B4
        n_bytes = int(sample_rate * 4.0)
        menu_samples = []
        for i in range(n_bytes):
            t = i / sample_rate
            # Slow LFO modulation (0.25 Hz)
            lfo = 0.5 + 0.5 * math.sin(2 * math.pi * 0.25 * t)
            val = sum(math.sin(2 * math.pi * f * t) for f in menu_freqs) / 4.0
            val *= 0.4 * lfo
            menu_samples.append(int(max(-1.0, min(1.0, val)) * 28000))
        menu_buf = struct.pack(f"<{len(menu_samples)}h", *menu_samples)
        self._music_tracks["bgm_menu"] = self._sound(menu_buf)

        # Track 2: bgm_explore (Sci-Fi Arpeggio - 4.0s loop)
        exp_notes = [220.0, 261.63, 329.63, 392.0, 440.0, 392.0, 329.63, 261.63]  # A-minor arpeggio
        exp_buf = b""
        note_dur = 500  # 500ms per note -> 8 notes = 4.0s
        for freq in exp_notes:
            exp_buf += self._make_samples(note_dur, freq, wave="sin", fade_out=True)
        self._music_tracks["bgm_explore"] = self._sound(exp_buf)

        # Track 3: bgm_combat (Tactical Battle Bassline - 3.2s loop)
        comb_notes = [110.0, 110.0, 130.81, 146.83, 110.0, 98.0, 110.0, 130.81]  # A2 bassline
        comb_buf = b""
        note_dur_c = 400  # 400ms per note -> 8 notes = 3.2s
        for freq in comb_notes:
            note_buf = self._make_samples(note_dur_c, freq, wave="saw", fade_out=True)
            perc_buf = self._make_samples(note_dur_c, 120.0, wave="noise", fade_out=True)
            comb_buf += self._mix(note_buf, perc_buf)
        self._music_tracks["bgm_combat"] = self._sound(comb_buf)

        # Track 4: bgm_boss (Dramatic Boss Fight - 3.2s loop)
        boss_notes = [65.41, 65.41, 69.30, 65.41, 73.42, 65.41, 69.30, 61.74]  # C2 dark bassline
        boss_buf = b""
        note_dur_b = 400
        for freq in boss_notes:
            b_buf = self._make_samples(note_dur_b, freq, wave="square", fade_out=True)
            pulse_buf = self._make_samples(note_dur_b, freq * 2, wave="saw", fade_out=True)
            boss_buf += self._mix(b_buf, pulse_buf)
        self._music_tracks["bgm_boss"] = self._sound(boss_buf)
