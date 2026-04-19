import pygame
import math
from settings import TILE

# Collision margin so the player doesn't clip into walls
MARGIN = 8


class Player:
    def __init__(self, x, y):
        self.x         = float(x)
        self.y         = float(y)
        self.angle     = 0.0
        self.speed     = 2
        self.rot_speed = 0.035
        self.health    = 100

    def move(self, keys, game_map):
        dx = math.cos(self.angle) * self.speed
        dy = math.sin(self.angle) * self.speed

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self._slide(dx, dy, game_map)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self._slide(-dx, -dy, game_map)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.angle -= self.rot_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.angle += self.rot_speed

    def rotate(self, d_angle):
        """Called from main loop on MOUSEMOTION."""
        self.angle += d_angle

    # ------------------------------------------------------------------
    def _passable(self, nx, ny, game_map):
        """True if the point (nx, ny) with a margin box is fully in open space."""
        rows = len(game_map)
        cols = len(game_map[0])
        for ox in (-MARGIN, MARGIN):
            for oy in (-MARGIN, MARGIN):
                c = int((nx + ox) / TILE)
                r = int((ny + oy) / TILE)
                if not (0 <= r < rows and 0 <= c < cols):
                    return False
                if game_map[r][c] == 1:
                    return False
        return True

    def _slide(self, dx, dy, game_map):
        """Try full move, then axis-only moves for wall sliding."""
        nx, ny = self.x + dx, self.y + dy
        if self._passable(nx, ny, game_map):
            self.x, self.y = nx, ny
        elif self._passable(self.x + dx, self.y, game_map):
            # Slide along X
            self.x += dx
        elif self._passable(self.x, self.y + dy, game_map):
            # Slide along Y
            self.y += dy
        # else: fully blocked, don't move

    # ------------------------------------------------------------------
    def draw(self, surface, mini_tile):
        px = int(self.x / TILE * mini_tile)
        py = int(self.y / TILE * mini_tile)
        pygame.draw.circle(surface, (255, 255, 0), (px, py), 5)
        ex = px + int(math.cos(self.angle) * 14)
        ey = py + int(math.sin(self.angle) * 14)
        pygame.draw.line(surface, (255, 255, 0), (px, py), (ex, ey), 2)
