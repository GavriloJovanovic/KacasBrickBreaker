"""
LeaderboardScreen — displays the top-10 high score table.

Call load() before switching to this screen.
If a new entry was just saved, pass highlight_rank so that row is highlighted.

handle_event() returns:
  "menu"  — any key or click → back to main menu
  None    — waiting
"""
import pygame
from scoreboard import load_scores
from ui import draw_text_centered, make_overlay

VIRTUAL_W = 800
VIRTUAL_H = 600

_WHITE    = (255, 255, 255)
_YELLOW   = (255, 220,  50)
_DIM      = ( 80,  90, 130)
_GOLD     = (255, 200,   0)
_SILVER   = (190, 200, 215)
_BRONZE   = (200, 130,  60)
_ROW_ALT  = ( 10,  14,  40)   # subtle alternating row tint
_ROW_HI   = ( 50,  60, 120)   # highlight for new entry


_RANK_COLORS = {
    0: _GOLD,
    1: _SILVER,
    2: _BRONZE,
}

_ROW_H    = 36    # height per leaderboard row in pixels
_TABLE_Y  = 148   # y of the first row
_COL_RANK = 90    # x of rank number
_COL_NAME = 160   # x of player name
_COL_SCORE = 620  # x of score (right-aligned)


class LeaderboardScreen:
    def __init__(self, bg: pygame.Surface):
        self.bg             = bg
        self.entries: list[tuple[str, int]] = []
        self.highlight_rank: int | None = None   # 0-based index to highlight
        self._fonts: dict | None = None

    # ------------------------------------------------------------------ #

    def load(self, highlight_rank: int | None = None):
        """
        Reload scores from disk and set the highlighted row.
        highlight_rank: 0-based index of the newly added entry, or None.
        """
        self.entries        = load_scores()
        self.highlight_rank = highlight_rank

    # ------------------------------------------------------------------ #

    def handle_event(self, event) -> str | None:
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            return "menu"
        return None

    # ------------------------------------------------------------------ #

    def draw(self, surface: pygame.Surface):
        fonts = self._get_fonts()

        # Background + overlay
        surface.blit(self.bg, (0, 0))
        surface.blit(make_overlay(VIRTUAL_W, VIRTUAL_H, alpha=145), (0, 0))

        # Title
        draw_text_centered(surface, "HIGH  SCORES", fonts["title"], _YELLOW, 68, shadow=True)
        pygame.draw.line(surface, (70, 100, 200), (100, 132), (700, 132), 1)

        # Column headers
        self._draw_header(surface, fonts)

        # Rows
        if not self.entries:
            draw_text_centered(surface, "NO  SCORES  YET  —  BE  THE  FIRST!",
                               fonts["row"], _DIM, _TABLE_Y + _ROW_H * 3)
        else:
            for i, (name, score) in enumerate(self.entries):
                self._draw_row(surface, fonts, i, name, score)

        # Footer
        draw_text_centered(surface, "PRESS  ANY  KEY  TO  CONTINUE",
                           fonts["hint"], _DIM, VIRTUAL_H - 30)

    # ------------------------------------------------------------------ #

    def _draw_header(self, surface: pygame.Surface, fonts: dict):
        hdr_y = _TABLE_Y - 24
        color = (100, 115, 180)
        surface.blit(fonts["label"].render("#",      False, color), (_COL_RANK  - 6, hdr_y))
        surface.blit(fonts["label"].render("NAME",   False, color), (_COL_NAME,      hdr_y))
        surface.blit(fonts["label"].render("SCORE",  False, color), (_COL_SCORE - 30, hdr_y))

    def _draw_row(self, surface: pygame.Surface, fonts: dict,
                  idx: int, name: str, score: int):
        y     = _TABLE_Y + idx * _ROW_H
        is_hi = (idx == self.highlight_rank)

        # Row background (alternating tint + highlight for new entry)
        row_color = _ROW_HI if is_hi else (_ROW_ALT if idx % 2 == 0 else (0, 0, 0, 0))
        if row_color != (0, 0, 0, 0):
            pygame.draw.rect(surface, row_color, (60, y - 2, VIRTUAL_W - 120, _ROW_H - 2))

        # Rank colour — gold / silver / bronze for top 3
        rank_color = _RANK_COLORS.get(idx, _WHITE if not is_hi else _YELLOW)
        text_color = _YELLOW if is_hi else _WHITE

        # Rank number
        rank_surf = fonts["row"].render(f"{idx + 1:02d}.", False, rank_color)
        surface.blit(rank_surf, (_COL_RANK - rank_surf.get_width(), y + 4))

        # Name
        name_surf = fonts["row"].render(name[:14], False, text_color)
        surface.blit(name_surf, (_COL_NAME, y + 4))

        # Score (right-aligned)
        score_surf = fonts["row"].render(f"{score:06d}", False, text_color)
        surface.blit(score_surf, (_COL_SCORE - score_surf.get_width(), y + 4))

        # Small star next to new entry
        if is_hi:
            star = fonts["label"].render("★ NEW", False, _YELLOW)
            surface.blit(star, (_COL_SCORE + 10, y + 6))

    # ------------------------------------------------------------------ #

    def _get_fonts(self) -> dict:
        if self._fonts is None:
            self._fonts = {
                "title": pygame.font.SysFont("Courier New", 42, bold=True),
                "row":   pygame.font.SysFont("Courier New", 20, bold=True),
                "label": pygame.font.SysFont("Courier New", 14, bold=False),
                "hint":  pygame.font.SysFont("Courier New", 15, bold=False),
            }
        return self._fonts
