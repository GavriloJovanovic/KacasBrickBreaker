# KacasBrickBreaker — Detailed Project Plan

## 1. System Environment

| Item | Value |
|---|---|
| OS | Windows 11 Pro |
| Python | 3.14.0 (via `python` / `py` command) |
| pip | 25.2 |
| tkinter | Built-in (confirmed working) |
| pygame | NOT installed — must be installed |
| Pillow | NOT installed — must be installed |

---

## 2. Technology Decisions

### Game Engine: **pygame**
- Best fit for a real-time arcade game (60 FPS game loop, pixel-level drawing, keyboard/mouse events, collision detection)
- Much more capable than tkinter Canvas for game development
- Supports image loading (background, sprites), pixel fonts, and fast rendering

### Image Handling: **Pillow (PIL)**
- Needed to pre-process and resize `background.jpg` and `brick-breaker.png` for pygame surfaces
- Used to scale assets to window resolution at startup

### Score Storage: **Plain text file**
- `scores/highscore.txt` — one record per line in format `NAME:SCORE`
- Top 10 scores sorted descending
- No database dependency — keeps it simple and portable

---

## 3. Installation Guide

### Step 1 — Verify Python
```bash
python --version
# Expected: Python 3.14.0
```

### Step 2 — Install required libraries
```bash
pip install pygame pillow
```

### Step 3 — Verify installs
```bash
python -c "import pygame; print(pygame.version.ver)"
python -c "from PIL import Image; print('Pillow OK')"
```

### Step 4 — Set up Git & GitHub
See **Phase 1** in Section 9 for the full step-by-step git setup (repo creation, init, first push).

---

## 4. Project Structure

```
KacasBrickBreaker/
├── main.py                  # Entry point — launches the app
├── game.py                  # Core game loop and state machine
├── menu.py                  # Main menu screen (START GAME / EXIT)
├── ball.py                  # Ball class (movement, speed, collision)
├── paddle.py                # Paddle class (mouse/keyboard control)
├── brick.py                 # Brick class (color, HP, pixel art draw)
├── brick_manager.py         # Manages brick grid, spawning, random generation
├── hud.py                   # HUD overlay (score, level, lives)
├── scoreboard.py            # Highscore read/write logic
├── name_input.py            # Name entry screen after game over
├── leaderboard_screen.py    # Displays top 10 scores
├── settings_screen.py       # Settings screen (display mode, paddle control)
├── settings.py              # Settings data class — load/save settings.json
├── assets/
│   ├── background.jpg       # Space pixel art background (menu + game)
│   └── brick-breaker.png    # Reference design (used for color palette)
├── scores/
│   └── highscore.txt        # Auto-created — stores top 10 NAME:SCORE
├── settings.json            # Auto-created — persists user settings
├── PLAN.md                  # This file
├── CLAUDE.md                # Claude AI skills/context file
├── .gitignore
└── requirements.txt         # pygame, pillow
```

---

## 5. Design & Visual Style

### Color Palette (from brick-breaker.png)
| Element | Color |
|---|---|
| Background | Dark navy `#0A0E2A` + space texture from `background.jpg` |
| Brick Row 1 | Red `#E53935` |
| Brick Row 2 | Orange `#FB8C00` |
| Brick Row 3 | Yellow `#FDD835` |
| Brick Row 4 | Green `#43A047` |
| Brick Row 5 | Cyan `#00ACC1` |
| Brick Row 6 | Blue `#1E88E5` |
| Ball | Light blue / white pixel circle |
| Paddle | Light grey with pixel outline |
| HUD text | White pixel font |

### Pixelated Style Rules
- All drawing uses **hard pixel edges** — no anti-aliasing
- Bricks have a **1px darker border** on bottom/right (depth effect)
- Font: `pygame.font.SysFont("Courier", size)` or load a pixel TTF font
- Ball rendered as a small square OR as a circle with pixel radius
- Background image scaled to window and tiled/cropped, rendered every frame

### Window Size & Display Mode
- **Default**: 800 × 600 px windowed
- **Fullscreen**: toggleable via Settings screen — uses `pygame.FULLSCREEN` flag with the native desktop resolution
- When fullscreen is active, all game elements scale proportionally using a virtual surface of 800×600 that is then `pygame.transform.scale()`-d to the real screen size
- Title (windowed mode): `"KacasBrickBreaker"`
- Toggle persisted in `settings.json` so the choice is remembered between sessions
- F11 key also toggles fullscreen at any time during the game

---

## 6. Game Mechanics — Full Specification

### 6.1 Ball
- Starts stationary above the paddle; launches on SPACE or click
- Initial speed: `5 px/frame` at 60 FPS
- Direction: 45° upward angle (random left or right)
- Bounces off: top wall, left wall, right wall, paddle, bricks
- When ball hits **bottom wall**: loses 1 life, ball resets to paddle position
- Speed increases each level (see Level System below)

### 6.2 Paddle
- Width: 100px, Height: 14px
- Clamped to window bounds
- Paddle y-position: fixed at `y = 560` (in virtual 800×600 space)
- **Control scheme is selected in Settings** — three options:
  | Option | Keys / Input |
  |---|---|
  | Mouse | Mouse horizontal position tracks paddle center |
  | Arrow Keys | LEFT / RIGHT arrow keys move paddle at fixed speed |
  | A / D Keys | A (left) / D (right) keys move paddle at fixed speed |
- Keyboard paddle speed: `8 px/frame` (scales with fullscreen virtual space)
- Control setting persisted in `settings.json`

### 6.3 Bricks
- Grid area: x from 40 to 760, y from 60 to ~320 (top half of screen)
- Brick size: `72px wide × 24px tall` with `4px gap`
- **Random generation over time**: every N seconds (decreasing with level), a new row of bricks drops in from the top, pushing existing ones down
- If any brick reaches the paddle line → **game over** (like Tetris-style danger)
- Each brick takes **1 hit** to break (standard bricks); higher levels may introduce **2-hit bricks** (slightly darker shade)
- Brick colors assigned by row (top row = hardest color, cycles through palette)

### 6.4 Level System
| Level | Bricks Broken Total | Ball Speed Multiplier | Spawn Rate (new row every X sec) |
|---|---|---|---|
| 1 | 0–19 | 1.0x (5 px/frame) | 20 sec |
| 2 | 20–39 | 1.2x | 17 sec |
| 3 | 40–59 | 1.4x | 14 sec |
| 4 | 60–79 | 1.6x | 11 sec |
| 5+ | 80+ (stays at 80-brick intervals) | +0.2x per level | -3 sec per level (min 5 sec) |

Level-up triggers: 20 bricks → level 2, 40 → level 3, 60 → level 4, 80 → level 5, 100 → level 6, etc.

### 6.5 Lives
- Start with **3 lives**
- Life lost when ball hits bottom
- Ball resets to paddle, waits for player to launch
- At 0 lives: **Game Over** screen appears

### 6.6 Scoring
- Each brick broken: **+10 points**
- Level bonus on level-up: **+100 points × new level**
- Score tracked in real time in HUD

---

## 7. Screen Flow / State Machine

```
MENU
 ├── START GAME → PLAYING
 │                  ├── LEVEL UP (visual flash, brief pause)
 │                  ├── GAME OVER → NAME INPUT → LEADERBOARD → MENU
 │                  └── PAUSE (ESC key) → MENU
 ├── SETTINGS → MENU
 └── EXIT → sys.exit()
```

### 7.1 Main Menu (`menu.py`)
- Background: `background.jpg` scaled to current resolution (handles fullscreen)
- Game title: `"KACAS BRICK BREAKER"` in large pixel font, centered top
- Three buttons: `[START GAME]`, `[SETTINGS]`, and `[EXIT]`
- Buttons styled as pixelated rectangles with hover highlight

### 7.2 Settings Screen (`settings_screen.py`)
- Same background as menu
- Title: `"SETTINGS"` in pixel font
- **Paddle Control** option (cycle through with click or LEFT/RIGHT):
  - `[MOUSE]` → `[ARROW KEYS]` → `[A / D KEYS]` → back to `[MOUSE]`
  - Currently selected option shown highlighted / different color
- **Display Mode** toggle:
  - `[WINDOWED]` ↔ `[FULLSCREEN]`
  - Switching fullscreen applies immediately (pygame display reinit)
- `[BACK]` button returns to main menu and saves settings to `settings.json`
- Settings auto-load on startup; if `settings.json` missing, defaults are: `windowed` + `mouse`

### `settings.json` Default Content
```json
{
  "fullscreen": false,
  "paddle_control": "mouse"
}
```
Valid values for `paddle_control`: `"mouse"`, `"arrows"`, `"ad"`

### 7.3 Name Input Screen (`name_input.py`)
- Shown after Game Over
- Displays final score
- Text input field for player name (max 12 characters)
- Confirm with ENTER key
- Only shown if score qualifies for top 10

### 7.4 Leaderboard Screen (`leaderboard_screen.py`)
- Shows top 10 NAME + SCORE
- Sorted by score descending
- Player's new entry highlighted
- Press any key to return to menu

---

## 8. Score File Format (`scores/highscore.txt`)

```
PlayerName:9999
AnotherGuy:8500
Kaca:7200
...
```

- Max 10 entries stored
- Auto-created on first run if missing
- Written atomically (write to temp then rename) to avoid corruption

---

## 9. Implementation Phases

### Phase 1 — Setup, Git & Skeleton

#### 1a — GitHub Repo (do this manually before writing any code)
1. Go to https://github.com/GavriloJovanovic → **New repository**
2. Name: `KacasBrickBreaker`, set Public or Private, **do NOT** initialize with README
3. Copy the repo URL: `https://github.com/GavriloJovanovic/KacasBrickBreaker.git`

#### 1b — Local Git Init
```bash
cd C:\Users\Gavrilo\Desktop\Files\WorkProjects\KacasBrickBreaker
git init
git remote add origin https://github.com/GavriloJovanovic/KacasBrickBreaker.git
git branch -M main
```

#### 1c — Project Files
- [ ] `.gitignore` (first file — before anything else is staged)
- [ ] `requirements.txt` with `pygame` and `pillow`
- [ ] `scores/` folder + `highscore.txt` auto-creation logic
- [ ] `settings.py` — Settings dataclass with load/save to `settings.json`
- [ ] `main.py` — reads settings, opens correct display mode (windowed/fullscreen), closes cleanly
- [ ] Virtual surface (800×600) → scale to real screen for fullscreen support
- [ ] F11 global fullscreen toggle wired up

#### 1d — First Commit & Push
```bash
git add .
git commit -m "Phase 1: project skeleton, settings, display init"
git push -u origin main
```

### Phase 2 — Main Menu & Settings
- [ ] `menu.py` with background image rendering (resolution-aware)
- [ ] Title text and three buttons (START GAME, SETTINGS, EXIT)
- [ ] Mouse hover and click detection
- [ ] `settings_screen.py` — paddle control selector + display mode toggle
- [ ] Settings saved to `settings.json` on BACK
- [ ] State transitions: menu → settings → menu, menu → game

### Phase 3 — Core Game Objects
- [ ] `ball.py` — Ball class with movement and wall bounce
- [ ] `paddle.py` — Paddle class supporting all three control schemes (reads from Settings)
- [ ] `brick.py` — Brick class with pixelated draw and hit detection
- [ ] `brick_manager.py` — Grid management and random row spawning

### Phase 4 — Game Loop
- [ ] `game.py` — Main game loop integrating ball, paddle, bricks
- [ ] Collision detection: ball vs paddle, ball vs bricks, ball vs walls
- [ ] Life loss on bottom wall hit, ball reset
- [ ] Score tracking and level-up logic
- [ ] HUD: score, level, lives display

### Phase 5 — Game Over Flow
- [ ] Game Over screen with final score
- [ ] `name_input.py` — name entry UI
- [ ] `scoreboard.py` — read/write/sort top 10
- [ ] `leaderboard_screen.py` — display top 10

### Phase 6 — Polish
- [ ] Level-up visual flash effect
- [ ] Pixelated font styling
- [ ] Sound effects (optional — pygame mixer)
- [ ] Smooth ball speed transitions
- [ ] Two-hit bricks at higher levels

### Phase 7 — Final Polish & GitHub
- [ ] Final code review
- [ ] Write `README.md` with install and run instructions
- [ ] `git add . && git commit -m "Phase 7: polish and final release" && git push`

---

## 10. Running the Game

```bash
cd C:\Users\Gavrilo\Desktop\Files\WorkProjects\KacasBrickBreaker
python main.py
```

---

## 11. Requirements File (`requirements.txt`)

```
pygame>=2.5.0
pillow>=10.0.0
```

Install:
```bash
pip install -r requirements.txt
```
