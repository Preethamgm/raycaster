import random
from settings import TILE


def generate_map(cols=18, rows=16):
    grid = [[1] * cols for _ in range(rows)]
    rooms = []
    attempts = 0

    while len(rooms) < 7 and attempts < 200:
        attempts += 1
        w = random.randint(3, 6)
        h = random.randint(3, 6)
        rx = random.randint(1, cols - w - 1)
        ry = random.randint(1, rows - h - 1)

        overlap = False
        for (ex, ey, ew, eh) in rooms:
            if (rx - 1 < ex + ew and rx + w + 1 > ex and
                    ry - 1 < ey + eh and ry + h + 1 > ey):
                overlap = True
                break

        if not overlap:
            rooms.append((rx, ry, w, h))
            for cy in range(ry, ry + h):
                for cx in range(rx, rx + w):
                    grid[cy][cx] = 0

    # Connect rooms with L-shaped corridors
    for i in range(len(rooms) - 1):
        x1 = rooms[i][0]   + rooms[i][2]   // 2
        y1 = rooms[i][1]   + rooms[i][3]   // 2
        x2 = rooms[i+1][0] + rooms[i+1][2] // 2
        y2 = rooms[i+1][1] + rooms[i+1][3] // 2

        cx, cy = x1, y1
        while cx != x2:
            grid[cy][cx] = 0
            cx += 1 if cx < x2 else -1
        while cy != y2:
            grid[cy][cx] = 0
            cy += 1 if cy < y2 else -1

    # Solid border
    for i in range(rows):
        grid[i][0] = grid[i][cols - 1] = 1
    for j in range(cols):
        grid[0][j] = grid[rows - 1][j] = 1

    return grid, rooms


def get_player_start(rooms):
    # FIX: use integer centre of the first room cell to avoid spawning in walls
    x, y, w, h = rooms[0]
    cx = x + w // 2
    cy = y + h // 2
    return (cx + 0.5) * TILE, (cy + 0.5) * TILE


def get_enemy_starts(rooms):
    result = []
    for (x, y, w, h) in rooms[1:]:
        cx = x + w // 2
        cy = y + h // 2
        result.append(((cx + 0.5) * TILE, (cy + 0.5) * TILE))
    return result
