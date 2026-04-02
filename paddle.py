"""
Paddle — input handling (mouse / arrow keys / A-D), drawing.

The paddle always lives in virtual 800x600 coordinate space.
Mouse coordinates from main.py are already mapped to virtual space.
"""
import pygame

VIRTUAL_W  = 800
PADDLE_Y   = 545        # top edge of paddle (virtual space)
PADDLE_W   = 100        # width in pixels
PADDLE_H   =  14        # height in pixels
KEYBOARD_SPEED = 8      # px / frame when using keyboard

_COLOR_FILL    = (190, 200, 215)   # Light silver
_COLOR_LIGHT   = (230, 240, 255)   # Top-left highlight
_COLOR_SHADOW  = ( 90, 100, 115)   # Bottom-right shadow
_COLOR_BORDER  = ( 60,  75, 110)   # Outer border


class Paddle:
    def __init__(self, settings):
        """settings: Settings instance — read paddle_control each frame."""
        self.settings = settings
        self.x: float = float((VIRTUAL_W - PADDLE_W) // 2)   # left edge
        self.y: int   = PADDLE_Y

    # ------------------------------------------------------------------ #
    # Update                                                              #
    # ------------------------------------------------------------------ #

    def update(self, virt_mouse: tuple[int, int]):
        """
        Move the paddle for this frame based on the active control scheme.
        virt_mouse: mouse position already mapped to virtual 800x600 space.
        """
        scheme = self.settings.paddle_control

        if scheme == "mouse":
            # Centre paddle on mouse x
            self.x = float(virt_mouse[0] - PADDLE_W // 2)

        elif scheme == "arrows":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.x -= KEYBOARD_SPEED
            if keys[pygame.K_RIGHT]:
                self.x += KEYBOARD_SPEED

        elif scheme == "ad":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.x -= KEYBOARD_SPEED
            if keys[pygame.K_d]:
                self.x += KEYBOARD_SPEED

        # Clamp — keep the paddle fully inside the virtual canvas
        self.x = max(0.0, min(float(VIRTUAL_W - PADDLE_W), self.x))

    # ------------------------------------------------------------------ #
    # Properties                                                          #
    # ------------------------------------------------------------------ #

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), self.y, PADDLE_W, PADDLE_H)

    # ------------------------------------------------------------------ #
    # Drawing                                                             #
    # ------------------------------------------------------------------ #

    def draw(self, surface: pygame.Surface):
        r = self.rect

        # Fill
        pygame.draw.rect(surface, _COLOR_FILL, r)

        # Top highlight line (1 px) — gives a lit-from-above look
        pygame.draw.line(surface, _COLOR_LIGHT,
                         (r.x + 1,     r.y),
                         (r.right - 2, r.y))

        # Left highlight line
        pygame.draw.line(surface, _COLOR_LIGHT,
                         (r.x, r.y + 1),
                         (r.x, r.bottom - 2))

        # Bottom shadow line
        pygame.draw.line(surface, _COLOR_SHADOW,
                         (r.x + 1,     r.bottom - 1),
                         (r.right - 1, r.bottom - 1))

        # Right shadow line
        pygame.draw.line(surface, _COLOR_SHADOW,
                         (r.right - 1, r.y + 1),
                         (r.right - 1, r.bottom - 1))

        # Outer border (1 px)
        pygame.draw.rect(surface, _COLOR_BORDER, r, 1)
