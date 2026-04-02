"""
KacasBrickBreaker — entry point.

Owns:
  - the pygame display (real screen surface)
  - the 800x600 virtual canvas (all drawing happens here, then scaled)
  - the top-level state machine: MENU | SETTINGS | GAME
  - F11 global fullscreen toggle

State transitions:
  menu  → game      : START GAME button
  menu  → settings  : SETTINGS button
  settings → menu   : BACK / ESC
  game  → menu      : ESC (paused → M) or game_over handled in Phase 5
  game  → game_over : Phase 5 adds name-input flow
"""
import sys
import os

import pygame

from settings        import Settings
from menu            import MenuScreen
from settings_screen import SettingsScreen
from game            import Game

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
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((VIRTUAL_W, VIRTUAL_H))


def load_background() -> pygame.Surface:
    base = os.path.dirname(os.path.abspath(__file__))
    raw  = pygame.image.load(os.path.join(base, "background.jpg")).convert()
    return pygame.transform.scale(raw, (VIRTUAL_W, VIRTUAL_H))


def ensure_scores_dir():
    os.makedirs("scores", exist_ok=True)
    path = os.path.join("scores", "highscore.txt")
    if not os.path.exists(path):
        open(path, "w").close()


def virtual_mouse(screen: pygame.Surface) -> tuple[int, int]:
    """Map real screen mouse pos → virtual 800x600 coordinates."""
    mx, my = pygame.mouse.get_pos()
    rw, rh = screen.get_size()
    return (mx * VIRTUAL_W // rw, my * VIRTUAL_H // rh)


def blit_virtual(screen: pygame.Surface, virtual: pygame.Surface):
    rw, rh = screen.get_size()
    if (rw, rh) == (VIRTUAL_W, VIRTUAL_H):
        screen.blit(virtual, (0, 0))
    else:
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

    # Build screens
    menu_screen     = MenuScreen(settings, bg)
    settings_screen = SettingsScreen(settings, bg)
    game_screen     = Game(settings, bg)

    state   = "menu"
    running = True

    while running:
        current_ms = pygame.time.get_ticks()
        vm         = virtual_mouse(screen)

        # ---------------------------------------------------------- #
        # Event handling                                              #
        # ---------------------------------------------------------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            # Global F11 toggle — any screen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                settings.fullscreen = not settings.fullscreen
                settings.save()
                screen = make_screen(settings.fullscreen)
                continue

            # ---- MENU ----
            if state == "menu":
                action = menu_screen.handle_event(event, vm)
                if action == "start":
                    state = "game"
                    game_screen.new_game(current_ms)
                elif action == "settings":
                    state = "settings"
                elif action == "exit":
                    running = False

            # ---- SETTINGS ----
            elif state == "settings":
                action = settings_screen.handle_event(event, vm)
                if action == "back":
                    state = "menu"
                elif action == "display_changed":
                    screen = make_screen(settings.fullscreen)

            # ---- GAME ----
            elif state == "game":
                action = game_screen.handle_event(event, vm)
                if action == "menu":
                    state = "menu"
                elif action == "game_over":
                    # Phase 5 will insert name-input / leaderboard here.
                    # For now: return to menu.
                    state = "menu"

        # ---------------------------------------------------------- #
        # Update (logic — runs once per frame, outside event loop)    #
        # ---------------------------------------------------------- #
        if state == "game":
            game_screen.update(current_ms, vm)

        # ---------------------------------------------------------- #
        # Draw                                                        #
        # ---------------------------------------------------------- #
        virtual.fill((10, 14, 42))

        if state == "menu":
            menu_screen.draw(virtual, vm)
        elif state == "settings":
            settings_screen.draw(virtual, vm)
        elif state == "game":
            game_screen.draw(virtual, vm)

        blit_virtual(screen, virtual)
        clock.tick(FPS)

    settings.save()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
