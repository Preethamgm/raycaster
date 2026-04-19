import pygame
import math

from settings import *
from map      import generate_map, get_player_start, get_enemy_starts
from player   import Player
from enemy    import Enemy
from textures import generate_wall_texture
from renderer import (cast_rays, draw_floor_ceiling, draw_sprites,
                      draw_minimap, draw_hud, draw_crosshair,
                      draw_hit_flash, draw_shoot_flash)

SHOOT_RANGE    = 600
HIT_FLASH      = 10
SHOOT_FLASH    = 6
MOUSE_SENS     = 0.002   # radians per pixel of mouse movement


def try_shoot(player, enemies, game_map):
    """
    Cast a ray down the centre of the screen.
    Returns the closest alive enemy that is hit before a wall, or None.
    """
    rows  = len(game_map)
    cols  = len(game_map[0])
    cos_a = math.cos(player.angle)
    sin_a = math.sin(player.angle)

    # Find wall distance first
    wall_dist = float(SHOOT_RANGE)
    for d in range(1, SHOOT_RANGE):
        rx = player.x + cos_a * d
        ry = player.y + sin_a * d
        c  = int(rx / TILE)
        r  = int(ry / TILE)
        if 0 <= r < rows and 0 <= c < cols:
            if game_map[r][c] == 1:
                wall_dist = d
                break
        else:
            wall_dist = d
            break

    best      = None
    best_dist = wall_dist

    for enemy in enemies:
        if not enemy.alive:
            continue
        dx   = enemy.x - player.x
        dy   = enemy.y - player.y
        dist = math.hypot(dx, dy)
        if dist >= best_dist:
            continue

        angle_to   = math.atan2(dy, dx)
        angle_diff = angle_to - player.angle
        while angle_diff >  math.pi: angle_diff -= 2 * math.pi
        while angle_diff < -math.pi: angle_diff += 2 * math.pi

        # FIX: compute angular half-width of the enemy sprite correctly.
        # The sprite world-size is ~TILE pixels wide; angular size = 2*atan(r/dist)
        # Use a simpler but accurate: half_angle = atan(TILE*0.4 / dist)
        corrected  = dist * math.cos(angle_diff)
        half_angle = math.atan2(TILE * 0.4, max(corrected, 1))

        if abs(angle_diff) < half_angle:
            best      = enemy
            best_dist = dist

    return best


def new_game():
    game_map, rooms = generate_map(cols=18, rows=16)
    px, py          = get_player_start(rooms)
    player          = Player(px, py)
    enemies         = [Enemy(ex, ey) for ex, ey in get_enemy_starts(rooms)]
    return game_map, player, enemies


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Raycaster — Python 3D Engine")
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("monospace", 14)

    wall_tex = generate_wall_texture()

    game_map, player, enemies = new_game()
    hit_timer = shoot_timer = kills = 0

    # FIX: capture mouse for smooth mouse-look
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    while True:
        # ── Events ────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_r:
                    game_map, player, enemies = new_game()
                    hit_timer = shoot_timer = kills = 0
                if event.key == pygame.K_SPACE and player.health > 0:
                    shoot_timer = SHOOT_FLASH
                    hit = try_shoot(player, enemies, game_map)
                    if hit:
                        hit.shoot()
                        if not hit.alive:
                            kills += 1

            # FIX: handle mouse look
            if event.type == pygame.MOUSEMOTION and player.health > 0:
                rel_x, _ = event.rel
                player.rotate(rel_x * MOUSE_SENS)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if player.health > 0:
                    shoot_timer = SHOOT_FLASH
                    hit = try_shoot(player, enemies, game_map)
                    if hit:
                        hit.shoot()
                        if not hit.alive:
                            kills += 1

        # ── Update ────────────────────────────────────────────────────
        keys = pygame.key.get_pressed()
        if player.health > 0:
            player.move(keys, game_map)

        for enemy in enemies:
            enemy.update(player, game_map)
            # FIX: only alive enemies can damage the player (not ragdolls)
            if enemy.alive:
                if math.hypot(enemy.x - player.x, enemy.y - player.y) < TILE * 0.42:
                    player.health = max(0, player.health - ENEMY_DAMAGE)
                    hit_timer     = HIT_FLASH

        # FIX: prune expired enemies AFTER damage checks so order is consistent
        enemies = [e for e in enemies if not e.expired]

        if hit_timer   > 0: hit_timer   -= 1
        if shoot_timer > 0: shoot_timer -= 1

        # ── Draw ──────────────────────────────────────────────────────
        screen.fill((0, 0, 0))
        draw_floor_ceiling(screen)
        z_buffer = cast_rays(screen, player, game_map, wall_tex)
        draw_sprites(screen, player, enemies, z_buffer)
        draw_minimap(screen, player, game_map, enemies)
        draw_hud(screen, player, font)
        draw_crosshair(screen)
        draw_hit_flash(screen, hit_timer)
        draw_shoot_flash(screen, shoot_timer)

        fps_s   = font.render(f"FPS {int(clock.get_fps())}", True, (200, 200, 200))
        hint_s  = font.render("WASD/Mouse: move   CLICK/SPACE: shoot   R: new map   ESC: quit",
                              True, (120, 120, 120))
        kills_s = font.render(f"KILLS  {kills}", True, (220, 180, 60))
        screen.blit(fps_s,   (MAP_WIDTH + FOV_WIDTH - 75, 10))
        screen.blit(hint_s,  (MAP_WIDTH + 10, 10))
        screen.blit(kills_s, (MAP_WIDTH + FOV_WIDTH - 120, HEIGHT - 32))

        if player.health <= 0:
            # Release mouse capture on death screen
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)

            ov   = pygame.Surface((FOV_WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 170))
            screen.blit(ov, (MAP_WIDTH, 0))
            dead = font.render("YOU DIED", True, (220, 50, 50))
            sub  = font.render(f"Kills: {kills}   Press R to respawn", True, (180, 180, 180))
            screen.blit(dead, (MAP_WIDTH + FOV_WIDTH // 2 - dead.get_width() // 2, HEIGHT // 2 - 20))
            screen.blit(sub,  (MAP_WIDTH + FOV_WIDTH // 2 - sub.get_width() // 2,  HEIGHT // 2 + 10))
        else:
            # Re-grab if player respawned
            if not pygame.event.get_grab():
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
