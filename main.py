"""
KacasBrickBreaker — entry point.

Owns:
  - the pygame display (real screen surface)
  - the 800x600 virtual canvas (all drawing happens here, then scaled)
  - the top-level state machine: MENU | SETTINGS | GAME (phases 3-4)
  - F11 global fullscreen toggle
"""
import sys
import os

import pygame

from settings        import Settings
from menu            import MenuScreen
from settings_screen import SettingsScreen

# ------------------------------------------------------------------ #
# Constants                                                           #
# ------------------------------------------------------------------ #
VIRTUAL_W = 800
VIRTUAL_H = 600
TITLE     = "KacasBrickBreaker"
FPS       = 60


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def make_screen(fullscreen: bool) -> pygame.Surface:
    """Create (or recreate) the real display surface."""
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((VIRTUAL_W, VIRTUAL_H))


def load_background() -> pygame.Surface:
    """Load and scale background.jpg to the virtual canvas size once."""
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "background.jpg")
    raw  = pygame.image.load(path).convert()
    return pygame.transform.scale(raw, (VIRTUAL_W, VIRTUAL_H))


def ensure_scores_dir():
    """Guarantee scores/ folder and highscore.txt exist."""
    os.makedirs("scores", exist_ok=True)
    path = os.path.join("scores", "highscore.txt")
    if not os.path.exists(path):
        open(path, "w").close()


def virtual_mouse(screen: pygame.Surface):
    """
    Map the real mouse position to virtual 800x600 coordinates.
    Required in fullscreen mode where the real resolution differs.
    """
    mx, my  = pygame.mouse.get_pos()
    rw, rh  = screen.get_size()
    return (mx * VIRTUAL_W // rw, my * VIRTUAL_H // rh)


def blit_virtual(screen: pygame.Surface, virtual: pygame.Surface):
    """Scale virtual canvas to the real screen and flip."""
    rw, rh = screen.get_size()
    if (rw, rh) == (VIRTUAL_W, VIRTUAL_H):
        screen.blit(virtual, (0, 0))
    else:
        # pygame.transform.scale (not smoothscale) preserves pixel art edges
        scaled = pygame.transform.scale(virtual, (rw, rh))
        screen.blit(scaled, (0, 0))
    pygame.display.flip()


# ------------------------------------------------------------------ #
# Main                                                                #
# ------------------------------------------------------------------ #

def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    settings = Settings()
    settings.load()

    ensure_scores_dir()

    screen  = make_screen(settings.fullscreen)
    virtual = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
    clock   = pygame.time.Clock()

    # Load shared assets once
    bg = load_background()

    # Screens
    menu_screen     = MenuScreen(settings, bg)
    settings_screen = SettingsScreen(settings, bg)

    # State machine
    # Valid states: "menu" | "settings" | "game"
    # "game" will be implemented in Phase 3-4
    state   = "menu"
    running = True

    # Placeholder font for the game stub (removed in Phase 4)
    _stub_font = None

    while running:
        vm = virtual_mouse(screen)   # Virtual mouse coords this frame

        # ---------------------------------------------------------- #
        # Event handling                                              #
        # ---------------------------------------------------------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            # Global F11 toggle — works from any screen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                settings.fullscreen = not settings.fullscreen
                settings.save()
                screen = make_screen(settings.fullscreen)
                continue

            # Delegate to the active screen
            if state == "menu":
                action = menu_screen.handle_event(event, vm)
                if action == "start":
                    state = "game"
                elif action == "settings":
                    state = "settings"
                elif action == "exit":
                    running = False

            elif state == "settings":
                action = settings_screen.handle_event(event, vm)
                if action == "back":
                    state = "menu"
                elif action == "display_changed":
                    # Fullscreen flag already toggled + saved inside SettingsScreen
                    screen = make_screen(settings.fullscreen)

            elif state == "game":
                # ESC from the game stub returns to menu
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "menu"

        # ---------------------------------------------------------- #
        # Drawing                                                     #
        # ---------------------------------------------------------- #
        virtual.fill((10, 14, 42))   # Base clear — dark navy

        if state == "menu":
            menu_screen.draw(virtual, vm)

        elif state == "settings":
            settings_screen.draw(virtual, vm)

        elif state == "game":
            # ---- Placeholder — replaced in Phase 4 ----
            if _stub_font is None:
                _stub_font = pygame.font.SysFont("Courier New", 26, bold=True)
            virtual.blit(bg, (0, 0))
            lines = [
                "GAME — coming in Phase 4",
                "",
                "Press ESC to return to menu",
            ]
            for i, line in enumerate(lines):
                surf = _stub_font.render(line, False, (255, 255, 255))
                virtual.blit(surf,
                             (VIRTUAL_W // 2 - surf.get_width() // 2,
                              VIRTUAL_H // 2 - 40 + i * 36))
            # -------------------------------------------

        blit_virtual(screen, virtual)
        clock.tick(FPS)

    settings.save()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
