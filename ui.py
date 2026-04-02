"""
Shared UI drawing helpers used by menu, settings, and other screens.
All coordinates are in virtual 800x600 space.
"""
import pygame

# Button palette
_BTN_FILL         = ( 15,  20,  55)
_BTN_FILL_HOVER   = ( 38,  50, 105)
_BTN_BORDER       = ( 70, 105, 200)
_BTN_BORDER_HOVER = (120, 165, 255)
_BTN_TEXT         = (255, 255, 255)

# Divider colour
DIVIDER_COLOR = (70, 100, 200)


def draw_button(surface, rect, text, font, hovered=False):
    """
    Draw a pixel-art style button (no rounded corners, no anti-alias text).
    rect: (x, y, w, h)  or a pygame.Rect
    """
    x, y, w, h = (rect.x, rect.y, rect.width, rect.height) \
                  if isinstance(rect, pygame.Rect) else rect

    fill   = _BTN_FILL_HOVER   if hovered else _BTN_FILL
    border = _BTN_BORDER_HOVER if hovered else _BTN_BORDER

    pygame.draw.rect(surface, fill,   (x, y, w, h))
    pygame.draw.rect(surface, border, (x, y, w, h), 2)

    # antialias=False keeps the pixel-art look
    label = font.render(text, False, _BTN_TEXT)
    surface.blit(label, (x + (w - label.get_width())  // 2,
                         y + (h - label.get_height()) // 2))


def draw_text_centered(surface, text, font, color, cy, shadow=True):
    """
    Draw text centred horizontally at vertical position cy.
    shadow=True adds a 2-px dark drop shadow for readability over the background.
    """
    if shadow:
        sh = font.render(text, False, (0, 0, 0))
        surface.blit(sh, (surface.get_width() // 2 - sh.get_width() // 2 + 2, cy + 2))
    surf = font.render(text, False, color)
    surface.blit(surf, (surface.get_width() // 2 - surf.get_width() // 2, cy))


def draw_label(surface, text, font, color, x, cy):
    """Draw left-aligned text vertically centred at cy."""
    surf = font.render(text, False, color)
    surface.blit(surf, (x, cy - surf.get_height() // 2))


def make_overlay(w, h, alpha=130):
    """Return a semi-transparent dark overlay Surface."""
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    ov.fill((0, 0, 10, alpha))
    return ov
