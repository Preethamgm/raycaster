import pygame
import math
import random

SPRING_ITERS = 3
DAMPING      = 0.97
BLOB_POINTS  = 8
S            = 64      # sprite canvas size

# Fade starts at frame 60, fully transparent at frame 92 (255/8 ≈ 32 frames)
FADE_START   = 60
FADE_RATE    = 8
EXPIRE_FRAME = 92      # must be > FADE_START + 255/FADE_RATE


class Point:
    __slots__ = ('x', 'y', 'px', 'py', 'fx', 'fy', 'mass')

    def __init__(self, x, y, mass=1.0):
        self.x = self.px = float(x)
        self.y = self.py = float(y)
        self.fx = self.fy = 0.0
        self.mass = mass

    def push(self, fx, fy):
        self.fx += fx
        self.fy += fy

    # Maximum displacement from origin — keeps ragdoll coords finite
    _CLAMP = 2000.0

    def step(self, gravity=0.0):
        vx = (self.x - self.px) * DAMPING
        vy = (self.y - self.py) * DAMPING
        self.px, self.py = self.x, self.y
        self.x += vx + self.fx / self.mass
        self.y += vy + self.fy / self.mass + gravity
        self.fx = self.fy = 0.0
        # FIX: clamp so coords never reach ±inf (causes OverflowError in int())
        if self.x >  self._CLAMP: self.x = self.px =  self._CLAMP
        if self.x < -self._CLAMP: self.x = self.px = -self._CLAMP
        if self.y >  self._CLAMP: self.y = self.py =  self._CLAMP
        if self.y < -self._CLAMP: self.y = self.py = -self._CLAMP


class Spring:
    __slots__ = ('a', 'b', 'rest', 'k')

    def __init__(self, a, b, k=0.8):
        self.a    = a
        self.b    = b
        self.rest = math.hypot(a.x - b.x, a.y - b.y)
        self.k    = k

    def resolve(self):
        dx   = self.b.x - self.a.x
        dy   = self.b.y - self.a.y
        dist = math.hypot(dx, dy)
        if dist < 0.001:
            return
        delta = (dist - self.rest) * self.k
        nx, ny = dx / dist, dy / dist
        self.a.push( nx * delta,  ny * delta)
        self.b.push(-nx * delta, -ny * delta)


class SoftBlob:
    """
    Physics-simulated blob sprite.
    Lives entirely in local 2D space around (0,0).
    Call update() every frame, get_sprite() to get the rendered surface.
    """

    def __init__(self, radius=18):
        self.radius      = radius
        self.health      = 3
        self.alive       = True
        self.squish      = 0
        self.death_timer = 0

        self._points  = []
        self._springs = []

        # FIX: Use a regular surface + manual per-pixel alpha instead of
        # SRCALPHA + set_alpha() which is ignored on SRCALPHA surfaces.
        self._surface     = pygame.Surface((S, S), pygame.SRCALPHA)
        self._fade_surf   = pygame.Surface((S, S), pygame.SRCALPHA)

        n = BLOB_POINTS
        self._centre = Point(0, 0, mass=3.0)
        self._points.append(self._centre)

        ring = []
        for i in range(n):
            angle = 2 * math.pi * i / n
            p = Point(math.cos(angle) * radius, math.sin(angle) * radius)
            ring.append(p)
            self._points.append(p)

        # Structural ring
        for i in range(n):
            self._springs.append(Spring(ring[i], ring[(i+1) % n], k=0.9))
        # Pressure springs centre ↔ ring
        for p in ring:
            self._springs.append(Spring(self._centre, p, k=0.25))
        # Shear springs skip-one
        for i in range(n):
            self._springs.append(Spring(ring[i], ring[(i+2) % n], k=0.15))

        self._ring = ring

    # ------------------------------------------------------------------
    def shoot(self):
        self.health -= 1
        self.squish  = 15
        for p in self._ring:
            d  = max(math.hypot(p.x - self._centre.x, p.y - self._centre.y), 1)
            nx = (p.x - self._centre.x) / d
            ny = (p.y - self._centre.y) / d
            p.push(nx * 14, ny * 14 - 6)
        if self.health <= 0:
            self._explode()

    def _explode(self):
        self.alive = False
        for p in self._points:
            p.push(random.uniform(-20, 20), random.uniform(-25, -5))

    # ------------------------------------------------------------------
    def update(self):
        if not self.alive:
            self.death_timer += 1

        # Idle wobble
        if self.alive and random.random() < 0.08:
            p = random.choice(self._ring)
            p.push(random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5))

        for _ in range(SPRING_ITERS):
            for s in self._springs:
                s.resolve()

        # Use gravity only when dead (ragdoll) so living blob doesn't droop
        grav = 0.3 if not self.alive else 0.0
        for p in self._points:
            p.step(gravity=grav)

        if self.squish > 0:
            self.squish -= 1

    # ------------------------------------------------------------------
    def get_sprite(self):
        surf = self._surface
        surf.fill((0, 0, 0, 0))

        scale = S / (self.radius * 2.8)
        half  = S // 2

        def to_px(p):
            x = int(half + p.x * scale)
            y = int(half + p.y * scale)
            return (max(0, min(S - 1, x)), max(0, min(S - 1, y)))

        pts = [to_px(p) for p in self._ring]

        if len(pts) >= 3:
            color   = (200, 40,  40) if self.alive else (70, 15, 15)
            outline = (255, 90,  90) if self.alive else (110, 35, 35)
            pygame.draw.polygon(surf, color,   pts)
            pygame.draw.polygon(surf, outline, pts, 2)

        if self.alive:
            avg_x = sum(p.x for p in self._ring) / len(self._ring)
            avg_y = sum(p.y for p in self._ring) / len(self._ring)
            for ex_off in (-5, 5):
                ex = int(half + (avg_x + ex_off) * scale)
                ey = int(half + (avg_y - 4)      * scale)
                ex = max(4, min(S - 5, ex))
                ey = max(4, min(S - 5, ey))
                pygame.draw.circle(surf, (255, 215,  0), (ex, ey), 4)
                pygame.draw.circle(surf, (  0,   0,  0), (ex + 1, ey + 1), 2)

        # FIX: Apply fade by modulating per-pixel alpha on the SRCALPHA surface.
        # set_alpha() is silently ignored on SRCALPHA surfaces, so we must
        # multiply the alpha channel directly via a BLEND_RGBA_MULT blit.
        if not self.alive and self.death_timer > FADE_START:
            alpha = max(0, 255 - (self.death_timer - FADE_START) * FADE_RATE)
            fade_mask = self._fade_surf
            fade_mask.fill((255, 255, 255, alpha))
            surf.blit(fade_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return surf

    # ------------------------------------------------------------------
    @property
    def expired(self):
        """True when the death animation is fully done — safe to remove."""
        # FIX: expire after EXPIRE_FRAME so the blob is fully invisible first
        return not self.alive and self.death_timer >= EXPIRE_FRAME
