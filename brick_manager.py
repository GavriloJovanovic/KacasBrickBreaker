"""
BrickManager — owns the entire brick grid.

Responsibilities:
  - Spawning new rows on a timer (rate increases with level)
  - Pushing all existing bricks down when a new row spawns
  - Ball-brick collision detection and response
  - Danger check (any brick reached the paddle zone?)
  - Drawing all bricks

Grid layout (virtual 800x600):
  9 bricks per row, each 72x24 px, 4-px gap between bricks.
  Total grid width = 9*72 + 8*4 = 680 px.
  Left margin = (800 - 680) // 2 = 60 px  → x: 60..740
  Top of grid  = 60 px  (below HUD)
"""
import random
import pygame

from brick import Brick

# ---------------------------------------------------------------------- #
# Grid constants                                                          #
# ---------------------------------------------------------------------- #
GRID_COLS  = 9
GRID_X     = 60    # x of leftmost column
GRID_Y     = 60    # y of the top row when first spawned
CELL_W     = 76    # Brick.W + gap  (72 + 4)
CELL_H     = 28    # Brick.H + gap  (24 + 4)
MIN_BRICKS = 5     # minimum bricks guaranteed per row

# The y coordinate above which bricks must stay (below = danger / game over)
# Paddle top is at y=545; we trigger at 5 px above that.
DANGER_Y   = 540


# ---------------------------------------------------------------------- #
# Spawn rate                                                              #
# ---------------------------------------------------------------------- #
def _spawn_interval_ms(level: int) -> int:
    """
    Milliseconds between automatic row spawns.
    Level 1 → 20 s, decreasing by 3 s per level, minimum 5 s.
    """
    seconds = max(5, 20 - (level - 1) * 3)
    return seconds * 1_000


# ---------------------------------------------------------------------- #
# Manager                                                                 #
# ---------------------------------------------------------------------- #
class BrickManager:

    def __init__(self):
        self.bricks: list[Brick] = []
        self.row_counter: int    = 0    # total rows ever spawned (drives colour cycle)
        self._last_spawn_ms: int = 0    # pygame ticks at last spawn

    # ------------------------------------------------------------------ #
    # Game lifecycle                                                      #
    # ------------------------------------------------------------------ #

    def start(self, current_ms: int):
        """
        Reset and pre-populate 3 rows so there are bricks to hit immediately.
        Call once when a new game begins.
        """
        self.bricks.clear()
        self.row_counter = 0
        for _ in range(3):
            self._spawn_row(level=1)
        self._last_spawn_ms = current_ms

    # ------------------------------------------------------------------ #
    # Per-frame update                                                    #
    # ------------------------------------------------------------------ #

    def update(self, level: int, current_ms: int):
        """Spawn a new row if the spawn timer has elapsed."""
        if current_ms - self._last_spawn_ms >= _spawn_interval_ms(level):
            self._spawn_row(level)
            self._last_spawn_ms = current_ms

    # ------------------------------------------------------------------ #
    # Collision                                                           #
    # ------------------------------------------------------------------ #

    def collide_ball(self, ball) -> int:
        """
        Test the ball against every active brick.

        Determines which face of the brick was hit (horizontal vs vertical)
        and flips the appropriate velocity component on the ball.
        Only ONE brick collision is resolved per call to prevent the ball
        from reversing twice in a single frame (tunnelling artefact).

        Returns the number of bricks destroyed.
        """
        destroyed = 0

        for brick in self.bricks:
            if not brick.active:
                continue
            if not ball.rect.colliderect(brick.rect):
                continue

            # Overlap on each axis tells us which face was struck.
            #   smaller overlap  →  the axis the ball entered from
            brick_cx = brick.x + Brick.W / 2
            brick_cy = brick.y + Brick.H / 2
            overlap_x = (Brick.W / 2 + ball.RADIUS) - abs(ball.x - brick_cx)
            overlap_y = (Brick.H / 2 + ball.RADIUS) - abs(ball.y - brick_cy)

            if overlap_x < overlap_y:
                ball.dx = -ball.dx   # left / right face → reverse horizontal
            else:
                ball.dy = -ball.dy   # top / bottom face  → reverse vertical

            if brick.hit():
                destroyed += 1

            break   # one collision per frame

        # Prune destroyed bricks from the list
        if destroyed:
            self.bricks = [b for b in self.bricks if b.active]

        return destroyed

    # ------------------------------------------------------------------ #
    # Danger check                                                        #
    # ------------------------------------------------------------------ #

    def check_danger(self) -> bool:
        """
        Return True if any brick has descended into the paddle zone.
        game.py should treat this as an immediate game over.
        """
        return any(b.active and b.y + Brick.H >= DANGER_Y for b in self.bricks)

    # ------------------------------------------------------------------ #
    # Drawing                                                             #
    # ------------------------------------------------------------------ #

    def draw(self, surface: pygame.Surface):
        for brick in self.bricks:
            brick.draw(surface)

    # ------------------------------------------------------------------ #
    # Utility                                                             #
    # ------------------------------------------------------------------ #

    def active_count(self) -> int:
        return sum(1 for b in self.bricks if b.active)

    # ------------------------------------------------------------------ #
    # Internal                                                            #
    # ------------------------------------------------------------------ #

    def _spawn_row(self, level: int):
        """
        Add a new row of bricks at the top of the grid.
        All existing bricks are shifted down by one cell height first.
        """
        # Push every existing brick down by one cell
        for b in self.bricks:
            b.y += CELL_H

        # Decide HP for this row's bricks
        # Level 3+: 30 % chance each individual brick is a 2-hit brick
        def _pick_hp() -> int:
            if level >= 3 and random.random() < 0.30:
                return 2
            return 1

        # Choose which columns appear — at least MIN_BRICKS, up to all 9
        present = [c for c in range(GRID_COLS) if random.random() < 0.85]
        if len(present) < MIN_BRICKS:
            present = random.sample(range(GRID_COLS), MIN_BRICKS)

        color_idx = self.row_counter % len(__import__("brick").BRICK_COLORS)

        for col in present:
            self.bricks.append(Brick(
                col=col,
                row=self.row_counter,
                x=GRID_X + col * CELL_W,
                y=GRID_Y,
                color_idx=color_idx,
                hp=_pick_hp(),
            ))

        self.row_counter += 1
