"""
NameInputScreen — shown after game over when the score earns a top-10 spot.

handle_event() returns:
  "confirm"  — player pressed ENTER with a non-empty name
  "skip"     — player pressed ESC (no name saved)
  None       — still typing
"""
import pygame
from ui import draw_text_centered, make_overlay

VIRTUAL_W = 800
VIRTUAL_H = 600
MAX_NAME  = 12   # character limit

_WHITE  = (255, 255, 255)
_YELLOW = (255, 220,  50)
_DIM    = ( 80,  90, 130)
_RED    = (220,  50,  50)
_BOX_BG = ( 12,  16,  45)
_BOX_BD = ( 70, 105, 200)
_BOX_BD_ACTIVE = (120, 165, 255)

# Characters allowed in a player name
_ALLOWED = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "0123456789 -_."
)


class NameInputScreen:
    def __init__(self, bg: pygame.Surface):
        self.bg    = bg
        self.name  = ""
        self.score = 0
        self._cursor_visible = True
        self._fonts: dict | None = None

    # ------------------------------------------------------------------ #

    def reset(self, score: int):
        """Call before switching to this screen."""
        self.name  = ""
        self.score = score

    # ------------------------------------------------------------------ #

    def handle_event(self, event) -> str | None:
        if event.type != pygame.KEYDOWN:
            return None

        key = event.key

        if key == pygame.K_RETURN:
            if self.name.strip():          # must have at least one non-space char
                self.name = self.name.strip()
                return "confirm"

        elif key == pygame.K_ESCAPE:
            return "skip"

        elif key == pygame.K_BACKSPACE:
            self.name = self.name[:-1]

        else:
            char = event.unicode
            if char in _ALLOWED and len(self.name) < MAX_NAME:
                self.name += char

        return None

    # ------------------------------------------------------------------ #

    def update(self, current_ms: int):
        """Blink the cursor — call every frame."""
        self._cursor_visible = (current_ms // 500) % 2 == 0

    # ------------------------------------------------------------------ #

    def draw(self, surface: pygame.Surface):
        fonts = self._get_fonts()

        # Background + overlay
        surface.blit(self.bg, (0, 0))
        surface.blit(make_overlay(VIRTUAL_W, VIRTUAL_H, alpha=150), (0, 0))

        # Header
        draw_text_centered(surface, "GAME  OVER",         fonts["big"],    _RED,    100, shadow=True)
        draw_text_centered(surface, "YOU  MADE  THE  TOP  10!",
                           fonts["medium"], _YELLOW, 175)
        draw_text_centered(surface, f"YOUR  SCORE:  {self.score:06d}",
                           fonts["medium"], _WHITE,  215)

        # Divider
        pygame.draw.line(surface, _BOX_BD, (150, 255), (650, 255), 1)

        # Prompt
        draw_text_centered(surface, "ENTER  YOUR  NAME:", fonts["label"], _DIM, 280)

        # Input box
        box_w, box_h = 360, 52
        box_x = (VIRTUAL_W - box_w) // 2
        box_y = 305
        pygame.draw.rect(surface, _BOX_BG, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surface, _BOX_BD_ACTIVE, (box_x, box_y, box_w, box_h), 2)

        # Name text inside box
        name_surf = fonts["input"].render(self.name, False, _WHITE)
        surface.blit(name_surf, (box_x + 14,
                                  box_y + (box_h - name_surf.get_height()) // 2))

        # Blinking cursor
        if self._cursor_visible and len(self.name) < MAX_NAME:
            cursor_x = box_x + 14 + name_surf.get_width() + 2
            cursor_y = box_y + 10
            pygame.draw.line(surface, _WHITE,
                             (cursor_x, cursor_y),
                             (cursor_x, box_y + box_h - 10), 2)

        # Character counter
        counter = fonts["hint"].render(
            f"{len(self.name)}/{MAX_NAME}", False, _DIM)
        surface.blit(counter, (box_x + box_w - counter.get_width() - 8,
                                box_y + box_h + 6))

        # Footer hints
        draw_text_centered(surface, "ENTER — confirm    ESC — skip",
                           fonts["hint"], _DIM, 400)

    # ------------------------------------------------------------------ #

    def _get_fonts(self) -> dict:
        if self._fonts is None:
            self._fonts = {
                "big":    pygame.font.SysFont("Courier New", 52, bold=True),
                "medium": pygame.font.SysFont("Courier New", 26, bold=True),
                "label":  pygame.font.SysFont("Courier New", 18, bold=False),
                "input":  pygame.font.SysFont("Courier New", 26, bold=True),
                "hint":   pygame.font.SysFont("Courier New", 15, bold=False),
            }
        return self._fonts
