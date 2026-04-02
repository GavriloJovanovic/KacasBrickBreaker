"""
Ball — physics, wall bouncing, paddle bouncing, drawing.

Coordinate system: virtual 800x600 canvas.
  x increases rightward, y increases downward (standard screen coords).
  So dy < 0 means moving UP.

The ball always has a valid (x, y) position.
When active=False it sits on the paddle; game.py keeps x/y synced to paddle.
"""
import math
import random
import pygame

VIRTUAL_W = 800
VIRTUAL_H = 600

_COLOR_BALL      = (144, 202, 249)   # Light blue  #90CAF9
_COLOR_HIGHLIGHT = (220, 235, 255)   # Near-white highlight dot


class Ball:
    RADIUS = 8   # pixels (in virtual space)

    def __init__(self):
        self.x: float = 400.0
        self.y: float = 540.0
        self.dx: float = 0.0
        self.dy: float = 0.0
        self.speed: float = 5.0   # px / frame
        self.active: bool = False  # False = sitting on paddle, waiting to launch

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def reset(self, x: float, y: float):
        """Place ball at (x, y) above paddle and mark as inactive."""
        self.x = float(x)
        self.y = float(y)
        self.dx = 0.0
        self.dy = 0.0
        self.active = False

    def launch(self):
        """
        Fire the ball upward at a random angle.
        Angle is chosen between 40° and 140° from horizontal to avoid
        near-horizontal and near-vertical shots.
        """
        # Randomly pick left or right half, avoiding straight-up (80-100°)
        # Left range: 40-80°  |  Right range: 100-140°
        side = random.choice(("left", "right"))
        if side == "right":
            angle_deg = random.uniform(40, 80)
        else:
            angle_deg = random.uniform(100, 140)

        angle = math.radians(angle_deg)
        self.dx =  math.cos(angle) * self.speed   # positive = right
        self.dy = -math.sin(angle) * self.speed   # negative = up (screen coords)
        self.active = True

    def set_speed(self, new_speed: float):
        """
        Change the ball speed while keeping its current direction.
        Safe to call whether the ball is active or not.
        """
        self.speed = new_speed
        if not self.active:
            return
        current = math.hypot(self.dx, self.dy)
        if current > 0:
            scale = new_speed / current
            self.dx *= scale
            self.dy *= scale

    # ------------------------------------------------------------------ #
    # Update                                                              #
    # ------------------------------------------------------------------ #

    def update(self) -> str | None:
        """
        Move the ball one frame.
        Handles left / right / top wall bounces.
        Returns:
          'bottom'  — ball fell below the screen (lose a life)
          None      — normal frame
        """
        if not self.active:
            return None

        self.x += self.dx
        self.y += self.dy

        r = self.RADIUS

        # Left wall
        if self.x - r < 0:
            self.x = float(r)
            self.dx = abs(self.dx)

        # Right wall
        elif self.x + r > VIRTUAL_W:
            self.x = float(VIRTUAL_W - r)
            self.dx = -abs(self.dx)

        # Top wall
        if self.y - r < 0:
            self.y = float(r)
            self.dy = abs(self.dy)

        # Bottom — fell off screen
        if self.y - r > VIRTUAL_H:
            return "bottom"

        return None

    # ------------------------------------------------------------------ #
    # Collision helpers                                                   #
    # ------------------------------------------------------------------ #

    def bounce_off_paddle(self, paddle_rect: pygame.Rect):
        """
        Reflect the ball off the paddle.
        The exit angle depends on WHERE the ball hits the paddle:
          - Centre hit  → mostly straight up
          - Edge hit    → steep angle toward that side
        This gives the player control over the ball direction.
        """
        # Normalised hit position: -1.0 (left edge) → 0.0 (centre) → +1.0 (right edge)
        paddle_cx = paddle_rect.x + paddle_rect.width / 2
        hit = (self.x - paddle_cx) / (paddle_rect.width / 2)
        hit = max(-1.0, min(1.0, hit))

        # Map to exit angle: ±60° from straight up
        angle = hit * math.radians(60)   # angle from the vertical axis
        self.dx =  math.sin(angle) * self.speed
        self.dy = -abs(math.cos(angle) * self.speed)   # always upward

        # Nudge ball above paddle so it doesn't collide again next frame
        self.y = float(paddle_rect.y - self.RADIUS - 1)

    # ------------------------------------------------------------------ #
    # Properties                                                          #
    # ------------------------------------------------------------------ #

    @property
    def rect(self) -> pygame.Rect:
        r = self.RADIUS
        return pygame.Rect(int(self.x) - r, int(self.y) - r, r * 2, r * 2)

    # ------------------------------------------------------------------ #
    # Drawing                                                             #
    # ------------------------------------------------------------------ #

    def draw(self, surface: pygame.Surface):
        cx, cy = int(self.x), int(self.y)
        r = self.RADIUS

        # Main ball circle
        pygame.draw.circle(surface, _COLOR_BALL, (cx, cy), r)

        # Small highlight dot (top-left quadrant) for pixel depth
        hx = cx - r // 3
        hy = cy - r // 3
        pygame.draw.circle(surface, _COLOR_HIGHLIGHT, (hx, hy), max(2, r // 4))
