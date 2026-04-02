# CLAUDE.md — KacasBrickBreaker Project Skills

This file gives Claude Code full context about the KacasBrickBreaker project so it can contribute effectively without re-discovering project details each session.

---

## Project Identity

- **Name**: KacasBrickBreaker
- **Type**: Windows desktop game (Python, pygame)
- **Owner**: GavriloJovanovic (GitHub: https://github.com/GavriloJovanovic)
- **Repo**: https://github.com/GavriloJovanovic/KacasBrickBreaker
- **Root**: `C:\Users\Gavrilo\Desktop\Files\WorkProjects\KacasBrickBreaker`

---

## Tech Stack

| Tool | Version | Notes |
|---|---|---|
| Python | 3.14.0 | Command: `python` or `py` |
| pygame-ce | >=2.5.7 | pygame Community Edition — drop-in replacement, has Python 3.14 wheel. Install: `pip install pygame-ce`. Import is still `import pygame`. |
| Pillow | >=10.0.0 | Must be installed via pip |
| tkinter | built-in | Available but NOT used — pygame is the game engine |
| pip | 25.2 | |

**Install command**: `pip install pygame pillow`

**Run command**: `python main.py`

---

## Project Structure

```
KacasBrickBreaker/
├── main.py                  # Entry point
├── game.py                  # Game loop + state machine
├── menu.py                  # Main menu (START GAME / EXIT)
├── ball.py                  # Ball physics class
├── paddle.py                # Paddle (mouse-controlled)
├── brick.py                 # Single brick rendering + HP
├── brick_manager.py         # Grid, row spawning logic
├── hud.py                   # Score/Level/Lives overlay
├── scoreboard.py            # highscore.txt read/write
├── name_input.py            # Name entry after game over
├── leaderboard_screen.py    # Top 10 display screen
├── settings_screen.py       # Settings screen (display mode, paddle control)
├── settings.py              # Settings dataclass — load/save settings.json
├── assets/
│   ├── background.jpg       # Space pixel art BG (used in menu + game)
│   └── brick-breaker.png    # Visual reference for style/colors
├── scores/
│   └── highscore.txt        # Auto-created, NAME:SCORE per line
├── settings.json            # Auto-created — persists fullscreen + paddle_control
├── PLAN.md                  # Full implementation plan
├── CLAUDE.md                # This file
├── requirements.txt         # pygame, pillow
└── .gitignore
```

---

## Visual Design Rules

- **Style**: Pixelated / retro arcade — NO anti-aliasing, NO smooth edges
- **Virtual canvas**: always 800 × 600 px — all game logic and drawing uses this coordinate space
- **Display**: windowed (800×600) or fullscreen (native resolution) — toggled in Settings or with F11; fullscreen uses `pygame.transform.scale()` from virtual canvas to real screen
- **Background**: `assets/background.jpg` scaled to current surface size, drawn every frame in both menu and game screens
- **Font**: Monospace pixel style — use `pygame.font.SysFont("Courier", size)` or load a .ttf pixel font
- **Brick colors by row** (top to bottom): Red → Orange → Yellow → Green → Cyan → Blue (cycles)
- **Bricks**: hard pixel edges, 1px darker border on bottom-right for depth effect
- **Ball**: small pixel circle or pixel square (~12px)
- **Paddle**: 100×14 px, light grey with pixel outline

### Color Reference (from brick-breaker.png)
- Background: `#0A0E2A`
- Red brick: `#E53935`
- Orange brick: `#FB8C00`
- Yellow brick: `#FDD835`
- Green brick: `#43A047`
- Cyan brick: `#00ACC1`
- Blue brick: `#1E88E5`
- Ball: `#90CAF9` (light blue)
- Paddle: `#CFD8DC`

---

## Game Mechanics Summary

### Ball
- Starts above paddle, launches on SPACE or mouse click
- Bounces off top/left/right walls, paddle, bricks
- Bottom wall hit = lose 1 life, ball resets to paddle
- Speed: starts at 5 px/frame, increases per level

### Paddle
- Horizontal only, fixed y = 560, width = 100px, height = 14px
- Clamped to virtual canvas bounds (x: 0 to 700)
- **Control scheme from Settings** (`settings.json` → `paddle_control`):
  - `"mouse"` — paddle center tracks mouse x (mapped to virtual canvas)
  - `"arrows"` — LEFT/RIGHT arrow keys, speed 8 px/frame
  - `"ad"` — A/D keys, speed 8 px/frame
- F11 key toggles fullscreen at any time

### Bricks
- Grid: x 40–760, y 60–320, brick size 72×24 with 4px gap
- New rows spawn from top on a timer (rate decreases per level)
- Bricks descend — if any brick reaches paddle line → Game Over
- Standard bricks: 1 hit; Level 3+ introduces 2-hit bricks (darker shade)
- Each brick broken: +10 points

### Level System
| Level | Total Bricks Broken | Speed | Spawn Interval |
|---|---|---|---|
| 1 | 0–19 | 5.0 | 20s |
| 2 | 20–39 | 6.0 | 17s |
| 3 | 40–59 | 7.0 | 14s |
| 4 | 60–79 | 8.0 | 11s |
| 5+ | +20 per level | +1.0 | -3s (min 5s) |

Level-up bonus: +100 × new_level points

### Lives
- Start: 3 lives
- Lost: ball hits bottom wall
- 0 lives: Game Over

### Score File (`scores/highscore.txt`)
- Format: `PlayerName:Score` (one per line)
- Max 10 entries, sorted descending by score
- Auto-created if missing on startup
- Name entry only shown if score qualifies for top 10
- Name input: max 12 characters, confirm with ENTER

---

## Screen State Machine

```
MENU → PLAYING → GAME OVER → NAME INPUT → LEADERBOARD → MENU
  ↓        ↓
SETTINGS  PAUSE (ESC)
  ↓
MENU
```

### Menu Screen
- Background: `assets/background.jpg`
- Title: `"KACAS BRICK BREAKER"` large pixel font, centered
- Buttons: `[START GAME]`, `[SETTINGS]`, and `[EXIT]` with hover highlight

### Settings Screen
- Same background as menu
- **Paddle Control** row: click to cycle `[MOUSE]` → `[ARROW KEYS]` → `[A / D KEYS]`
- **Display Mode** row: click to toggle `[WINDOWED]` ↔ `[FULLSCREEN]` (applies immediately)
- `[BACK]` saves to `settings.json` and returns to menu
- Defaults if `settings.json` missing: `fullscreen: false`, `paddle_control: "mouse"`

### Game Over Screen
- Shows final score
- Transitions to Name Input if score is top-10 worthy

### Name Input Screen
- Simple text field, max 12 chars
- ENTER to confirm, BACKSPACE to delete

### Leaderboard Screen
- Top 10, newest entry highlighted
- Any key to return to menu

---

## Coding Conventions

- All game classes are in their own file (one class per file)
- `game.py` imports and coordinates all classes — it is the single game loop owner
- `main.py` only: initializes pygame, creates the game controller, calls `game.run()`
- State management via a simple string enum: `"MENU"`, `"PLAYING"`, `"PAUSED"`, `"GAME_OVER"`, `"NAME_INPUT"`, `"LEADERBOARD"`
- No external config files — all constants defined at top of each file or in a `constants.py`
- Score file writes are atomic: write to temp file, then rename/replace
- All assets loaded once at startup and stored as pygame Surface objects

---

## What NOT to Do

- Do NOT use tkinter — pygame is the rendering engine
- Do NOT add sound unless explicitly asked (optional feature)
- Do NOT make the window freely resizable — only windowed (800×600) or fullscreen
- Do NOT add a database — only `scores/highscore.txt`
- Do NOT draw directly to the real screen surface — always draw to the 800×600 virtual surface, then scale
- Do NOT smooth/blur graphics — keep everything pixelated (use `pygame.transform.scale`, not `smoothscale`)

---

## GitHub

- Repo: https://github.com/GavriloJovanovic/KacasBrickBreaker
- Branch: `main`
- Remote: `origin`
- Push command: `git push origin main`
- Never force push without asking the user

---

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run game
python main.py

# Git workflow
git add .
git commit -m "Your message"
git push origin main
```
