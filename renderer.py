import pygame
import math
from settings import *


def cast_rays(surface, player, game_map, wall_tex):
    rows      = len(game_map)
    cols      = len(game_map[0])
    z_buffer  = []

    # FIX: centre each ray in its pixel column to avoid a half-step overshoot
    half_step = (FOV / NUM_RAYS) / 2
    ray_angle = player.angle - FOV / 2 + half_step

    for ray in range(NUM_RAYS):
        cos_a = math.cos(ray_angle)
        sin_a = math.sin(ray_angle)
        dist  = 0
        hit   = False
        rx = ry = 0.0

        while dist < MAX_DEPTH and not hit:
            dist += 1
            rx = player.x + cos_a * dist
            ry = player.y + sin_a * dist
            c  = int(rx / TILE)
            r  = int(ry / TILE)
            if 0 <= r < rows and 0 <= c < cols:
                if game_map[r][c] == 1:
                    hit = True
            else:
                hit = True

        corrected = dist * math.cos(ray_angle - player.angle)
        corrected = max(corrected, 1)          # never zero / negative
        z_buffer.append(corrected)

        wall_h = min(HEIGHT, (TILE * HEIGHT) // corrected)

        if abs(cos_a) > abs(sin_a):
            tex_x = int((ry % TILE) / TILE * TEX_SIZE) % TEX_SIZE
        else:
            tex_x = int((rx % TILE) / TILE * TEX_SIZE) % TEX_SIZE

        if wall_h > 0:
            col_s = wall_tex.subsurface((tex_x, 0, 1, TEX_SIZE))
            col_s = pygame.transform.scale(col_s, (1, wall_h))
            shade = max(30, 255 - int(corrected * 0.38))
            col_s.fill((shade, shade, shade), special_flags=pygame.BLEND_RGB_MULT)
            surface.blit(col_s, (MAP_WIDTH + ray, HALF_HEIGHT - wall_h // 2))

        ray_angle += FOV / NUM_RAYS

    return z_buffer


def draw_floor_ceiling(surface):
    """Fast gradient floor/ceiling — no per-pixel sampling."""
    for y in range(HALF_HEIGHT):
        t = y / HALF_HEIGHT
        s = int(10 + t * 40)
        pygame.draw.line(surface, (s, s, int(s * 1.8)),
                         (MAP_WIDTH, y), (WIDTH - 1, y))
    for y in range(HALF_HEIGHT, HEIGHT):
        t = (y - HALF_HEIGHT) / HALF_HEIGHT
        s = int(15 + t * 55)
        pygame.draw.line(surface, (s, s, s),
                         (MAP_WIDTH, y), (WIDTH - 1, y))


def draw_sprites(surface, player, enemies, z_buffer):
    # Sort back-to-front so closer sprites draw on top
    visible = sorted(
        enemies,
        key=lambda e: -math.hypot(e.x - player.x, e.y - player.y)
    )

    for enemy in visible:
        dx       = enemy.x - player.x
        dy       = enemy.y - player.y
        distance = math.hypot(dx, dy)
        if distance < 1:
            continue

        angle_to   = math.atan2(dy, dx)
        angle_diff = angle_to - player.angle
        while angle_diff >  math.pi: angle_diff -= 2 * math.pi
        while angle_diff < -math.pi: angle_diff += 2 * math.pi

        if abs(angle_diff) > FOV * 0.75:
            continue

        corrected = max(distance * math.cos(angle_diff), 1)
        spr_h     = min(HEIGHT * 2, int((TILE * HEIGHT) / corrected))
        spr_w     = spr_h

        if spr_h <= 0:
            continue

        center_col = int((angle_diff / FOV + 0.5) * FOV_WIDTH)
        start_x    = center_col - spr_w // 2
        top        = HALF_HEIGHT - spr_h // 2

        # Get fresh physics sprite this frame
        raw    = enemy.sprite
        scaled = pygame.transform.scale(raw, (spr_w, spr_h))

        # FIX: instead of a slow per-column loop (up to 700 blits per enemy),
        # build a single list of visible columns from the z-buffer, then do
        # ONE blit per contiguous visible run.  This eliminates flickering
        # caused by the previous approach's massive per-frame overhead.
        col_start = max(0, start_x)
        col_end   = min(FOV_WIDTH, start_x + spr_w)

        if col_start >= col_end:
            continue

        # Find contiguous runs of columns that pass the z-buffer test
        run_start = None
        for col in range(col_start, col_end + 1):   # +1 to flush last run
            passes = (col < col_end and
                      col < len(z_buffer) and
                      corrected < z_buffer[col])
            if passes and run_start is None:
                run_start = col
            elif not passes and run_start is not None:
                # Blit just this run as one rectangular strip
                run_w  = col - run_start
                src_x  = run_start - start_x
                strip  = scaled.subsurface((src_x, 0, run_w, spr_h))
                surface.blit(strip, (MAP_WIDTH + run_start, top))
                run_start = None


def draw_minimap(surface, player, game_map, enemies):
    rows = len(game_map)
    cols = len(game_map[0])
    mt   = min(MAP_WIDTH // cols, HEIGHT // rows)

    for r in range(rows):
        for c in range(cols):
            color = (55, 55, 55) if game_map[r][c] == 1 else (170, 170, 170)
            pygame.draw.rect(surface, color, (c * mt, r * mt, mt - 1, mt - 1))

    for enemy in enemies:
        enemy.draw_on_map(surface, mt)
    player.draw(surface, mt)


def draw_hud(surface, player, font):
    bw, bh = 200, 18
    x, y   = MAP_WIDTH + 12, HEIGHT - 32
    pygame.draw.rect(surface, (70, 0, 0),      (x, y, bw, bh))
    hw = int(bw * max(player.health, 0) / 100)
    pygame.draw.rect(surface, (210, 35, 35),   (x, y, hw, bh))
    pygame.draw.rect(surface, (220, 220, 220), (x, y, bw, bh), 1)
    surface.blit(font.render(f"HP  {int(player.health)}", True, (255, 255, 255)),
                 (x + 6, y + 2))


def draw_crosshair(surface):
    cx = MAP_WIDTH + FOV_WIDTH // 2
    cy = HEIGHT // 2
    pygame.draw.line(surface, (255, 255, 255), (cx - 10, cy), (cx + 10, cy), 1)
    pygame.draw.line(surface, (255, 255, 255), (cx, cy - 10), (cx, cy + 10), 1)


def draw_hit_flash(surface, timer):
    if timer > 0:
        ov = pygame.Surface((FOV_WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((200, 0, 0, min(160, timer * 8)))
        surface.blit(ov, (MAP_WIDTH, 0))


def draw_shoot_flash(surface, timer):
    if timer > 0:
        ov = pygame.Surface((FOV_WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((255, 255, 200, min(120, timer * 15)))
        surface.blit(ov, (MAP_WIDTH, 0))
