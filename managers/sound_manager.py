import math
import struct
import pygame


class SoundManager:
    """Procedural sound effects engine — generates all SFX from waveforms."""

    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        self._cache: dict[str, pygame.mixer.Sound] = {}
        self._enabled: bool = True
        self._volume: float = 0.5
        self._generate_all()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def play(self, name: str) -> None:
        if not self._enabled:
            return
        snd = self._cache.get(name)
        if snd:
            snd.set_volume(self._volume)
            snd.play()

    def toggle(self) -> bool:
        self._enabled = not self._enabled
        return self._enabled

    @property
    def enabled(self) -> bool:
        return self._enabled

    # ------------------------------------------------------------------
    # Waveform generation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_samples(duration_ms: int, freq: float, *, fade_out: bool = True,
                      wave: str = "sin", sample_rate: int = 22050) -> bytes:
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

            # Fade-out envelope
            if fade_out:
                envelope = max(0.0, 1.0 - i / n_samples)
                val *= envelope

            # Clamp & convert to 16-bit signed
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
        self._cache["laser_fire"] = self._sound(
            self._make_samples(180, 880, wave="square")
        )

        # --- Missile fire ---
        self._cache["missile_fire"] = self._sound(
            self._make_samples(300, 220, wave="saw")
        )

        # --- Beam fire ---
        self._cache["beam_fire"] = self._sound(
            self._make_samples(400, 600, wave="sin")
        )

        # --- Flak fire ---
        raw_flak = self._make_samples(200, 150, wave="noise", fade_out=True)
        self._cache["flak_fire"] = self._sound(raw_flak)

        # --- Shield hit ---
        self._cache["shield_hit"] = self._sound(
            self._make_samples(120, 1200, wave="sin")
        )

        # --- Hull hit ---
        raw_hit = self._make_samples(160, 100, wave="noise", fade_out=True)
        self._cache["hull_hit"] = self._sound(raw_hit)

        # --- Explosion (enemy destroyed) ---
        raw_exp = self._make_samples(500, 60, wave="noise", fade_out=True)
        self._cache["explosion"] = self._sound(raw_exp)

        # --- Button click ---
        self._cache["click"] = self._sound(
            self._make_samples(50, 1400, wave="sin")
        )

        # --- Jump / travel ---
        self._cache["jump"] = self._sound(
            self._make_samples(350, 440, wave="sin", fade_out=True)
        )

        # --- Purchase / shop ---
        self._cache["purchase"] = self._sound(
            self._make_samples(200, 660, wave="sin")
        )

        # --- Warning / alarm ---
        raw_a = self._make_samples(300, 500, wave="square", fade_out=False)
        raw_b = self._make_samples(300, 400, wave="square", fade_out=False)
        self._cache["alarm"] = self._sound(raw_a + raw_b)

        # --- Crew death ---
        self._cache["crew_death"] = self._sound(
            self._make_samples(250, 200, wave="saw", fade_out=True)
        )

        # --- Repair ---
        self._cache["repair"] = self._sound(
            self._make_samples(150, 1000, wave="sin")
        )

        # --- Door toggle ---
        self._cache["door"] = self._sound(
            self._make_samples(80, 300, wave="square")
        )

        # --- Victory fanfare ---
        notes = [523, 659, 784, 1047]  # C5-E5-G5-C6
        fanfare = b""
        for freq in notes:
            fanfare += self._make_samples(200, freq, wave="sin", fade_out=False)
        self._cache["victory"] = self._sound(fanfare)

        # --- Game over ---
        go = self._make_samples(600, 150, wave="saw", fade_out=True)
        self._cache["game_over"] = self._sound(go)
