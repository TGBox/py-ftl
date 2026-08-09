from typing import TYPE_CHECKING

    
import math
import random
import pygame

if TYPE_CHECKING:
    from game import Game


class Particle:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: tuple[int, int, int],
        radius: float,
        life: float,
        p_type: str = "spark",
        grow_rate: float = 0.0,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.life = life
        self.max_life = life
        self.p_type = p_type
        self.grow_rate = grow_rate

    def update(self, dt: float) -> bool:
        self.life -= dt
        if self.life <= 0.0:
            return False

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.radius += self.grow_rate * dt

        if self.p_type == "smoke":
            self.vy -= 8.0 * dt  # Gentle upward drift for smoke
            self.vx *= 0.96
        elif self.p_type == "spark":
            self.vx *= 0.92  # Air drag on sparks
            self.vy *= 0.92

        return True


class ParticleManager:
    """Visual FX Engine managing particle creation, physics updates, and alpha rendering."""

    def __init__(self):
        self.particles: list[Particle] = []
        self.game: Game | None = None   # Set by Game after construction

    def clear(self):
        self.particles.clear()

    def emit_explosion(self, x: float, y: float, count: int = 30):
        # 1. Core fireball particles
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(30.0, 180.0)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            col = random.choice([(255, 80, 20), (255, 160, 40), (255, 230, 80), (200, 40, 20)])
            rad = random.uniform(6.0, 14.0)
            life = random.uniform(0.3, 0.7)
            self.particles.append(Particle(x, y, vx, vy, col, rad, life, p_type="fire", grow_rate=6.0))

        # 2. Bright high-speed metal sparks
        for _ in range(count // 2):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(120.0, 320.0)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            col = (255, 255, 180)
            rad = random.uniform(2.0, 4.0)
            life = random.uniform(0.2, 0.5)
            self.particles.append(Particle(x, y, vx, vy, col, rad, life, p_type="spark"))

        # 3. Expanding dark smoke
        for _ in range(count // 3):
            vx = random.uniform(-20.0, 20.0)
            vy = random.uniform(-30.0, -10.0)
            col = (60, 65, 75)
            rad = random.uniform(8.0, 16.0)
            life = random.uniform(0.6, 1.2)
            self.particles.append(Particle(x, y, vx, vy, col, rad, life, p_type="smoke", grow_rate=10.0))

    def emit_shield_ripple(self, x: float, y: float, color: tuple[int, int, int] = (0, 220, 255), count: int = 18):
        for i in range(count):
            ang = (i / count) * 2 * math.pi + random.uniform(-0.1, 0.1)
            spd = random.uniform(80.0, 150.0)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            rad = random.uniform(3.0, 7.0)
            life = random.uniform(0.25, 0.45)
            self.particles.append(Particle(x, y, vx, vy, color, rad, life, p_type="shield"))

    def emit_sparks(self, x: float, y: float, count: int = 12):
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(60.0, 200.0)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            col = random.choice([(255, 220, 100), (255, 140, 40), (255, 255, 200)])
            rad = random.uniform(2.0, 4.0)
            life = random.uniform(0.2, 0.4)
            self.particles.append(Particle(x, y, vx, vy, col, rad, life, p_type="spark"))

    def emit_thruster(self, x: float, y: float, direction_x: float = 0.0, direction_y: float = 1.0):
        vx = direction_x * random.uniform(30.0, 70.0) + random.uniform(-10.0, 10.0)
        vy = direction_y * random.uniform(40.0, 90.0) + random.uniform(-5.0, 5.0)
        col = random.choice([(0, 200, 255), (100, 230, 255), (0, 140, 255)])
        rad = random.uniform(3.0, 7.0)
        life = random.uniform(0.15, 0.35)
        self.particles.append(Particle(x, y, vx, vy, col, rad, life, p_type="thruster"))

    def emit_smoke(self, x: float, y: float):
        vx = random.uniform(-10.0, 10.0)
        vy = random.uniform(-25.0, -10.0)
        col = (80, 85, 95)
        rad = random.uniform(5.0, 10.0)
        life = random.uniform(0.5, 0.9)
        self.particles.append(Particle(x, y, vx, vy, col, rad, life, p_type="smoke", grow_rate=8.0))

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface):
        if not self.particles:
            return

        for p in self.particles:
            alpha_ratio = max(0.0, min(1.0, p.life / p.max_life))
            alpha = int(255 * alpha_ratio)

            if p.radius <= 0.5:
                continue

            r = max(1, int(p.radius))
            p_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            color_with_alpha = (p.color[0], p.color[1], p.color[2], alpha)

            pygame.draw.circle(p_surf, color_with_alpha, (r, r), r)
            surface.blit(p_surf, (int(p.x) - r, int(p.y) - r))
