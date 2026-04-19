import math

# --- Window ---
WIDTH, HEIGHT = 1200, 500
MAP_WIDTH     = 220          # minimap panel width
FOV_WIDTH     = WIDTH - MAP_WIDTH
FPS           = 60

# --- World ---
TILE          = 50
TEX_SIZE      = 64

# --- Raycasting ---
FOV           = math.pi / 3
NUM_RAYS      = FOV_WIDTH
MAX_DEPTH     = 800
HALF_HEIGHT   = HEIGHT // 2

# --- Enemy ---
ENEMY_SPEED   = 0.7
ENEMY_DAMAGE  = 0.25
PATH_REFRESH  = 25
