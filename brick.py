"""
Brick — a single brick tile.

Visual style: pixel-art flat rectangle with 1-px light top/left edge
and 1-px dark bottom/right edge for a shallow 3-D look.

HP:
  1 — standard brick (destroyed in one hit)
  2 — reinforced brick (appears darker; turns normal colour when at 1 HP)
"""
import pygame

# Colour palette (from brick-breaker.png reference)
BRICK_COLORS = [
    (229,  57,  53),   # 0 Red    #E53935
    (251, 140,   0),   # 1 Orange #FB8C00
    (253, 216,  53),   # 2 Yellow #FDD835
    ( 67, 160,  71),   # 3 Green  #43A047
    (  0, 172, 193),   # 4 Cyan   #00ACC1
    ( 30, 136, 229),   # 5 Blue   #1E88E5
]

W = 72    # brick width  (pixels in virtual space)
H = 24    # brick height


def _lighten(color: tuple, amt: int = 55) -> tuple:
    return tuple(min(255, c + amt) for c in color)


def _darken(color: tuple, amt: int = 55) -> tuple:
    return tuple(max(0, c - amt) for c in color)


class Brick:
    W = W
    H = H

    def __init__(self, col: int, row: int, x: int, y: int,
                 color_idx: int, hp: int = 1):
        self.col       = col
        self.row       = row
        self.x         = x
        self.y         = y
        self.hp        = hp
        self.max_hp    = hp
        self.color_idx = color_idx
        self.active    = True

    # ------------------------------------------------------------------ #

    def hit(self) -> bool:
        """
        Apply one hit.
        Returns True if the brick is destroyed (hp reached 0).
        """
        self.hp -= 1
        if self.hp <= 0:
            self.active = False
            return True
        return False

    # ------------------------------------------------------------------ #

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, W, H)

    def _base_color(self) -> tuple:
        """Return the fill colour, dimmed if this is a damaged 2-hit brick."""
        base = BRICK_COLORS[self.color_idx % len(BRICK_COLORS)]
        if self.max_hp == 2 and self.hp == 1:
            # Damaged 2-hit brick — visibly darker to signal it needs another hit
            return _darken(base, 65)
        return base

    # ------------------------------------------------------------------ #

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        color = self._base_color()
        r     = self.rect

        # --- Fill ---
        pygame.draw.rect(surface, color, r)

        # --- Top & left highlight (lighter) ---
        light = _lighten(color, 60)
        pygame.draw.line(surface, light, (r.x,     r.y),        (r.right - 2, r.y))         # top
        pygame.draw.line(surface, light, (r.x,     r.y),        (r.x,         r.bottom - 2)) # left

        # --- Bottom & right shadow (darker) ---
        dark = _darken(color, 60)
        pygame.draw.line(surface, dark,  (r.x + 1, r.bottom - 1), (r.right - 1, r.bottom - 1)) # bottom
        pygame.draw.line(surface, dark,  (r.right - 1, r.y + 1),  (r.right - 1, r.bottom - 1)) # right

        # --- Crack overlay for 2-hit bricks at 1 HP ---
        if self.max_hp == 2 and self.hp == 1:
            self._draw_crack(surface, r)

    def _draw_crack(self, surface: pygame.Surface, r: pygame.Rect):
        """Draw a simple pixel crack to show the brick is damaged."""
        crack_color = (20, 10, 10)
        cx = r.x + r.width  // 2
        cy = r.y + r.height // 2
        # A small zigzag line through the centre of the brick
        points = [
            (cx - 8, cy - 8),
            (cx - 2, cy - 2),
            (cx + 3, cy - 6),
            (cx + 5, cy + 2),
            (cx + 9, cy + 8),
        ]
        pygame.draw.lines(surface, crack_color, False, points, 1)
