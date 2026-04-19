import pygame
import math
import heapq
from settings import TILE, ENEMY_SPEED, PATH_REFRESH
from softbody  import SoftBlob


class Enemy:
    """
    A* pathfinding brain wrapped around a SoftBlob physics sprite.
    world x/y = position in the game map (pixels).
    The blob always simulates in local (0,0) space for rendering.
    """

    def __init__(self, x, y):
        self.x      = float(x)
        self.y      = float(y)
        self.speed  = ENEMY_SPEED
        self.alive  = True
        self.path   = []
        self._timer = PATH_REFRESH   # FIX: trigger immediate first path
        self._blob  = SoftBlob()

    @property
    def sprite(self):
        return self._blob.get_sprite()

    @property
    def health(self):
        return self._blob.health

    @property
    def expired(self):
        """Remove from enemies list once ragdoll animation finishes."""
        return self._blob.expired

    def shoot(self):
        self._blob.shoot()
        if not self._blob.alive:
            self.alive = False

    # ------------------------------------------------------------------
    @staticmethod
    def _h(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _astar(self, game_map, start, goal):
        rows = len(game_map)
        cols = len(game_map[0])

        # FIX: if goal is inside a wall, find the nearest passable tile
        gr, gc = goal
        if not (0 <= gr < rows and 0 <= gc < cols and game_map[gr][gc] == 0):
            best_goal = None
            best_dist = float('inf')
            for r in range(max(0, gr - 2), min(rows, gr + 3)):
                for c in range(max(0, gc - 2), min(cols, gc + 3)):
                    if game_map[r][c] == 0:
                        d = abs(r - gr) + abs(c - gc)
                        if d < best_dist:
                            best_dist = d
                            best_goal = (r, c)
            if best_goal is None:
                return []
            goal = best_goal

        # FIX: also validate start tile
        sr, sc = start
        if not (0 <= sr < rows and 0 <= sc < cols and game_map[sr][sc] == 0):
            return []

        if start == goal:
            return []

        heap = [(0, start)]
        came = {}
        g    = {start: 0}

        while heap:
            _, cur = heapq.heappop(heap)
            if cur == goal:
                path = []
                while cur in came:
                    path.append(cur)
                    cur = came[cur]
                path.reverse()
                return path
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nb   = (cur[0] + dr, cur[1] + dc)
                r, c = nb
                if 0 <= r < rows and 0 <= c < cols and game_map[r][c] == 0:
                    ng = g[cur] + 1
                    if nb not in g or ng < g[nb]:
                        g[nb]    = ng
                        heapq.heappush(heap, (ng + self._h(nb, goal), nb))
                        came[nb] = cur
        return []

    # ------------------------------------------------------------------
    def update(self, player, game_map):
        # Physics always runs even after death (ragdoll)
        self._blob.update()

        if not self.alive:
            return

        self._timer += 1
        if self._timer >= PATH_REFRESH:
            self._timer = 0
            start = (int(self.y / TILE), int(self.x / TILE))
            goal  = (int(player.y / TILE), int(player.x / TILE))
            self.path = self._astar(game_map, start, goal)

        if self.path:
            tr, tc = self.path[0]
            tx     = (tc + 0.5) * TILE
            ty     = (tr + 0.5) * TILE
            dx     = tx - self.x
            dy     = ty - self.y
            dist   = math.hypot(dx, dy)

            # FIX: pop waypoint when close enough, even if path becomes empty
            if dist < self.speed + 2:
                self.path.pop(0)
                # immediately start moving toward the next waypoint this frame
                if self.path:
                    tr, tc = self.path[0]
                    tx     = (tc + 0.5) * TILE
                    ty     = (tr + 0.5) * TILE
                    dx     = tx - self.x
                    dy     = ty - self.y
                    dist   = math.hypot(dx, dy)

            if dist > 0.001:
                move_x = (dx / dist) * self.speed
                move_y = (dy / dist) * self.speed
                self.x += move_x
                self.y += move_y
                # Nudge centre mass to create walk wobble
                self._blob._centre.push(move_x * 0.5, move_y * 0.5)

    def draw_on_map(self, surface, mini_tile):
        if self.alive:
            ex = int(self.x / TILE * mini_tile)
            ey = int(self.y / TILE * mini_tile)
            pygame.draw.circle(surface, (220, 30, 30), (ex, ey), 5)
