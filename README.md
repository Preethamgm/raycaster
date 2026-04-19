# 🎮 Raycaster — A Python 3D Engine From Scratch

> Built with pure Python and Pygame. No Unity. No Unreal. No shortcuts.

---

## What Is This?

A fully functional first-person 3D shooter — written entirely in Python, from a blank file.

No game engine. No drag-and-drop editor. No tutorials that hand you the answer.  
Just math, physics, pathfinding algorithms, and a lot of debugging at 2am.

The same technique that powered **DOOM in 1993** — called **raycasting** — reimplemented by hand in 2025.

---

## What's Actually Going On Under The Hood

This isn't "I followed a YouTube tutorial" territory. Here's what was built from scratch:

- 🔭 **Raycasting renderer** — shoots hundreds of rays per frame to fake 3D perspective from a 2D map
- 🧠 **A\* Pathfinding** — enemies navigate around walls using the same algorithm used in professional games and Google Maps
- 🫧 **Soft-body physics** — enemies are simulated as spring-mass systems; they wobble when they walk and ragdoll when they die
- 🗺️ **Procedural map generation** — every new game generates a completely random dungeon with connected rooms
- 🎯 **3D sprite rendering with Z-buffering** — enemies are depth-sorted and occluded correctly behind walls
- ⚡ **Physics simulation** — Verlet integration, spring constraints, damping, impulse forces
- 🧱 **Procedural textures** — brick wall patterns generated in code, no image files needed

---

## Features

| Feature | Details |
|---|---|
| 3D Rendering | Raycasting with textured walls and distance shading |
| Enemy AI | A* pathfinding that recalculates routes in real time |
| Soft-body Enemies | Spring-mass physics, squish on hit, ragdoll on death |
| Procedural Maps | Random dungeon generation every run |
| Mouse Look | Smooth first-person camera control |
| Wall Sliding | Proper collision with axis-separated movement |
| Minimap | Live overhead view with player and enemy positions |
| HUD | Health bar, kill counter, shoot flash, hit flash |

---

## How To Run

**1. Install dependencies**
```bash
pip install pygame-ce
```

**2. Clone and run**
```bash
git clone https://github.com/preethamgm/raycaster.git
cd raycaster
python main.py
```

That's it. No `.exe` installer. No 40GB download. No account required.

---

## Controls

| Key / Input | Action |
|---|---|
| `W A S D` | Move |
| `Mouse` | Look around |
| `Left Click` or `Space` | Shoot |
| `R` | Generate new map |
| `ESC` | Quit |

---

## Project Structure

```
raycaster/
├── main.py          # Game loop — ties everything together
├── settings.py      # All constants and configuration
├── map.py           # Procedural dungeon generation
├── player.py        # Player movement and collision
├── enemy.py         # Enemy AI and A* pathfinding
├── softbody.py      # Spring-mass physics simulation
├── renderer.py      # Full 3D rendering pipeline
└── textures.py      # Procedural wall texture generation
```

---

## The Honest Truth

Most people who say *"I want to build a game engine from scratch"* open a YouTube video, get overwhelmed by the math, and go back to Unity.

This project actually shipped.

Every bug was hunted down. Every physics explosion that sent enemies flying to infinity was fixed. Every flickering sprite, broken pathfinder, and invisible wall was debugged line by line until it worked.

If you're reading this README, you're looking at what it looks like when someone actually finishes the thing.

---

## What I Learned

- How raycasting produces the illusion of 3D from a 2D grid
- How Verlet integration works for stable physics simulation
- How A* pathfinding finds optimal routes through arbitrary mazes
- How Z-buffering prevents sprites from drawing through walls
- How soft-body constraints produce organic, wobbly movement
- How procedural generation can create infinite unique levels
- That `set_alpha()` is silently ignored on `SRCALPHA` surfaces in Pygame (the hard way)

---

## Built With

- **Python 3.14**
- **Pygame-CE 2.5.7**
- **Math** — a lot of it

---

*Made from scratch. Bugs fixed by hand. Pushed to GitHub through sheer persistence.*
