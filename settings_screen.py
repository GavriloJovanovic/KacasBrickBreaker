"""
Settings screen.
Lets the player choose paddle control scheme and display mode.

Returns:
  "back"             — user pressed BACK or ESC  (settings already saved)
  "display_changed"  — fullscreen toggle applied  (main.py must recreate screen)
  None               — no state change
"""
import pygame
from ui import draw_button, draw_text_centered, make_overlay, DIVIDER_COLOR

VIRTUAL_W = 800
VIRTUAL_H = 600

_TITLE_COLOR    = (255, 220,  50)
_LABEL_COLOR    = (160, 175, 230)
_HINT_COLOR     = ( 75,  88, 140)
_SECTION_COLOR  = (120, 140, 200)

# Layout y-positions (centred design: label row above value button)
_SEC1_LABEL_Y = 185     # "PADDLE CONTROL" text
_SEC1_BTN_Y   = 215     # clickable value button
_SEC2_LABEL_Y = 315     # "DISPLAY MODE" text
_SEC2_BTN_Y   = 345     # clickable value button
_BACK_Y       = 475

_BTN_W  = 240
_BTN_H  =  50
_BTN_X  = (VIRTUAL_W - _BTN_W) // 2   # centred

_BACK_W = 160
_BACK_X = (VIRTUAL_W - _BACK_W) // 2


class SettingsScreen:
    def __init__(self, settings, bg: pygame.Surface):
        """
        settings : Settings instance (mutated by this screen)
        bg       : pre-loaded + pre-scaled background surface (800x600)
        """
        self.settings = settings
        self.bg = bg
        self._load_fonts()
        self._build_rects()

    # ------------------------------------------------------------------ #

    def _load_fonts(self):
        self.font_title  = pygame.font.SysFont("Courier New", 44, bold=True)
        self.font_label  = pygame.font.SysFont("Courier New", 18, bold=False)
        self.font_btn    = pygame.font.SysFont("Courier New", 20, bold=True)
        self.font_hint   = pygame.font.SysFont("Courier New", 15, bold=False)

    def _build_rects(self):
        self.ctrl_rect = pygame.Rect(_BTN_X, _SEC1_BTN_Y, _BTN_W, _BTN_H)
        self.disp_rect = pygame.Rect(_BTN_X, _SEC2_BTN_Y, _BTN_W, _BTN_H)
        self.back_rect = pygame.Rect(_BACK_X, _BACK_Y,   _BACK_W, _BTN_H)

    # ------------------------------------------------------------------ #

    def handle_event(self, event, virt_mouse):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.settings.save()
            return "back"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Cycle through paddle control options
            if self.ctrl_rect.collidepoint(virt_mouse):
                self.settings.next_control()
                return None

            # Toggle fullscreen — signal main.py to recreate the display
            if self.disp_rect.collidepoint(virt_mouse):
                self.settings.fullscreen = not self.settings.fullscreen
                self.settings.save()
                return "display_changed"

            # Back to menu — save and exit
            if self.back_rect.collidepoint(virt_mouse):
                self.settings.save()
                return "back"

        return None

    def draw(self, surface, virt_mouse):
        # 1. Background + overlay
        surface.blit(self.bg, (0, 0))
        surface.blit(make_overlay(VIRTUAL_W, VIRTUAL_H, alpha=140), (0, 0))

        # 2. Title
        draw_text_centered(surface, "SETTINGS", self.font_title, _TITLE_COLOR, 68)
        pygame.draw.line(surface, DIVIDER_COLOR, (150, 138), (650, 138), 2)

        # 3. Section 1 — Paddle Control
        self._draw_section_label(surface, "PADDLE CONTROL", _SEC1_LABEL_Y)
        draw_button(surface, self.ctrl_rect,
                    self.settings.control_label(), self.font_btn,
                    hovered=self.ctrl_rect.collidepoint(virt_mouse))

        # Small hint under the button
        self._draw_hint(surface, "click to cycle options",
                        _SEC1_BTN_Y + _BTN_H + 6)

        # 4. Section 2 — Display Mode
        self._draw_section_label(surface, "DISPLAY MODE", _SEC2_LABEL_Y)
        disp_label = "FULLSCREEN" if self.settings.fullscreen else "WINDOWED"
        draw_button(surface, self.disp_rect, disp_label, self.font_btn,
                    hovered=self.disp_rect.collidepoint(virt_mouse))

        self._draw_hint(surface, "click to toggle",
                        _SEC2_BTN_Y + _BTN_H + 6)

        # 5. Back button
        draw_button(surface, self.back_rect, "< BACK", self.font_btn,
                    hovered=self.back_rect.collidepoint(virt_mouse))

        # 6. ESC hint
        esc = self.font_hint.render("ESC = back to menu", False, _HINT_COLOR)
        surface.blit(esc, (VIRTUAL_W // 2 - esc.get_width() // 2, VIRTUAL_H - 28))

    # ------------------------------------------------------------------ #

    def _draw_section_label(self, surface, text, y):
        surf = self.font_label.render(text, False, _LABEL_COLOR)
        surface.blit(surf, (VIRTUAL_W // 2 - surf.get_width() // 2, y))

    def _draw_hint(self, surface, text, y):
        surf = self.font_hint.render(text, False, _HINT_COLOR)
        surface.blit(surf, (VIRTUAL_W // 2 - surf.get_width() // 2, y))
