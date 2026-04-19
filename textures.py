import pygame
import random
from settings import TEX_SIZE


def generate_wall_texture():
    tex = pygame.Surface((TEX_SIZE, TEX_SIZE))
    tex.fill((90, 80, 75))
    brick_h = 16
    brick_w = 32
    palette = [(190, 100, 75), (165, 85, 65), (175, 92, 70), (185, 95, 72)]
    for row in range(TEX_SIZE // brick_h + 1):
        offset = (brick_w // 2) if row % 2 == 1 else 0
        for col in range(-1, TEX_SIZE // brick_w + 2):
            bx    = col * brick_w + offset
            by    = row * brick_h
            base  = palette[(row * 3 + col) % len(palette)]
            v     = random.randint(-15, 15)
            color = tuple(max(0, min(255, c + v)) for c in base)
            pygame.draw.rect(tex, color, (bx + 1, by + 1, brick_w - 2, brick_h - 2))
    return tex
