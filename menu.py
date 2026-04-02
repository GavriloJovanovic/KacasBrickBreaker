"""
Main menu screen.
Returns one of: "start" | "settings" | "exit"
"""
import pygame
from ui import draw_button, draw_text_centered, make_overlay, DIVIDER_COLOR

VIRTUAL_W = 800
VIRTUAL_H = 600

# Title colours
_TITLE_COLOR    = (255, 220,  50)   # Golden yellow
_VERSION_COLOR  = ( 75,  88, 140)   # Muted blue-grey

# Button layout
_BTN_W       = 270
_BTN_H       =  52
_BTN_X       = (VIRTUAL_W - _BTN_W) // 2   # Horizontally centred
_BTN_START_Y = 255
_BTN_GAP     =  20

_BUTTONS = [
    ("START GAME", "start"),
    ("SETTINGS",   "settings"),
    ("EXIT",       "exit"),
]


class MenuScreen:
    def __init__(self, settings, bg: pygame.Surface):
        """
        settings : Settings instance (read-only here)
        bg       : pre-loaded + pre-scaled background surface (800x600)
        """
        self.settings = settings
        self.bg = bg
        self._load_fonts()
        self._build_rects()

    # ------------------------------------------------------------------ #

    def _load_fonts(self):
        self.font_title   = pygame.font.SysFont("Courier New", 52, bold=True)
        self.font_btn     = pygame.font.SysFont("Courier New", 22, bold=True)
        self.font_version = pygame.font.SysFont("Courier New", 15, bold=False)

    def _build_rects(self):
        self.btn_rects = []
        for i in range(len(_BUTTONS)):
            y = _BTN_START_Y + i * (_BTN_H + _BTN_GAP)
            self.btn_rects.append(pygame.Rect(_BTN_X, y, _BTN_W, _BTN_H))

    # ------------------------------------------------------------------ #

    def handle_event(self, event, virt_mouse):
        """Return action string on click, else None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, (_, action) in zip(self.btn_rects, _BUTTONS):
                if rect.collidepoint(virt_mouse):
                    return action
        return None

    def draw(self, surface, virt_mouse):
        # 1. Background
        surface.blit(self.bg, (0, 0))

        # 2. Dark overlay so buttons are readable over the busy BG
        surface.blit(make_overlay(VIRTUAL_W, VIRTUAL_H, alpha=110), (0, 0))

        # 3. Title  — two lines for visual impact
        draw_text_centered(surface, "KACAS",         self.font_title, _TITLE_COLOR,  78)
        draw_text_centered(surface, "BRICK BREAKER", self.font_title, _TITLE_COLOR, 140)

        # 4. Decorative divider under title
        pygame.draw.line(surface, DIVIDER_COLOR, (180, 215), (620, 215), 2)

        # 5. Buttons
        for rect, (label, _) in zip(self.btn_rects, _BUTTONS):
            draw_button(surface, rect, label, self.font_btn,
                        hovered=rect.collidepoint(virt_mouse))

        # 6. Subtle version / hint line at bottom
        hint = self.font_version.render("F11 = TOGGLE FULLSCREEN", False, _VERSION_COLOR)
        surface.blit(hint, (VIRTUAL_W // 2 - hint.get_width() // 2, VIRTUAL_H - 28))
