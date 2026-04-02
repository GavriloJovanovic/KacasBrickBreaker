"""
HUD — draws the top status bar: Score | Level | Lives.

Occupies the top 50 px of the virtual canvas (brick grid starts at y=60).
"""
import pygame

VIRTUAL_W  = 800
HUD_H      = 50
_BG_COLOR  = (6, 8, 28)       # Very dark navy strip
_TEXT_COLOR = (220, 225, 255)  # Soft white
_DIM_COLOR  = (80, 90, 130)   # Muted — used for labels
_HEART_FULL = (220, 40, 40)    # Red heart
_HEART_LOST = (50, 30, 30)     # Dark / empty heart


def _draw_heart(surface: pygame.Surface, cx: int, cy: int, full: bool):
    """
    Draw a small pixel heart centred at (cx, cy).
    full=True → red  |  full=False → dark (lost life)
    """
    color = _HEART_FULL if full else _HEART_LOST
    s = 8   # half-size of the bounding box

    # Two top lobes (circles)
    pygame.draw.circle(surface, color, (cx - s // 2, cy - 1), s // 2)
    pygame.draw.circle(surface, color, (cx + s // 2, cy - 1), s // 2)

    # Lower triangle pointing down
    pts = [
        (cx - s,       cy + 1),
        (cx + s,       cy + 1),
        (cx,           cy + s + 2),
    ]
    pygame.draw.polygon(surface, color, pts)


class HUD:
    def __init__(self):
        self.font_value = pygame.font.SysFont("Courier New", 22, bold=True)
        self.font_label = pygame.font.SysFont("Courier New", 13, bold=False)

    def draw(self, surface: pygame.Surface, score: int, level: int, lives: int,
             max_lives: int = 3):
        # --- Background strip ---
        pygame.draw.rect(surface, _BG_COLOR, (0, 0, VIRTUAL_W, HUD_H))
        pygame.draw.line(surface, (40, 55, 120),
                         (0, HUD_H - 1), (VIRTUAL_W, HUD_H - 1), 1)

        # --- Score (left) ---
        self._draw_labeled(surface, "SCORE", f"{score:06d}", x=20, cy=25)

        # --- Level (centre) ---
        self._draw_labeled(surface, "LEVEL", str(level), x=VIRTUAL_W // 2 - 30, cy=25)

        # --- Lives (right) — drawn as pixel hearts ---
        lbl = self.font_label.render("LIVES", False, _DIM_COLOR)
        surface.blit(lbl, (VIRTUAL_W - 130, 8))

        for i in range(max_lives):
            cx = VIRTUAL_W - 120 + i * 36
            _draw_heart(surface, cx, 35, full=(i < lives))

    # ------------------------------------------------------------------ #

    def _draw_labeled(self, surface, label: str, value: str, x: int, cy: int):
        lbl_surf = self.font_label.render(label, False, _DIM_COLOR)
        val_surf = self.font_value.render(value,  False, _TEXT_COLOR)
        surface.blit(lbl_surf, (x, cy - lbl_surf.get_height() - 1))
        surface.blit(val_surf, (x, cy))
