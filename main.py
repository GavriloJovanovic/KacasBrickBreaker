"""
KacasBrickBreaker — entry point.

State machine:
  menu → game → name_input → leaderboard → menu
       → settings → menu
  game → menu  (pause → M, or ESC from waiting)
  game → leaderboard (game over, score too low for top 10)
"""
import sys
import os

import pygame

from settings          import Settings
from menu              import MenuScreen
from settings_screen   import SettingsScreen
from game              import Game
from name_input        import NameInputScreen
from leaderboard_screen import LeaderboardScreen
import scoreboard

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

    bg = load_background()

    # Build all screens once — reused for the whole session
    menu_screen        = MenuScreen(settings, bg)
    settings_screen    = SettingsScreen(settings, bg)
    game_screen        = Game(settings, bg)
    name_input_screen  = NameInputScreen(bg)
    leaderboard_screen = LeaderboardScreen(bg)

    state   = "menu"
    running = True

    while running:
        current_ms = pygame.time.get_ticks()
        vm         = virtual_mouse(screen)

        # ---------------------------------------------------------- #
        # Events                                                      #
        # ---------------------------------------------------------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            # Global F11 — any screen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                settings.fullscreen = not settings.fullscreen
                settings.save()
                screen = make_screen(settings.fullscreen)
                continue

            # ---- MENU ----
            if state == "menu":
                action = menu_screen.handle_event(event, vm)
                if action == "start":
                    game_screen.new_game(current_ms)
                    state = "game"
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
                    final_score = game_screen.score
                    if scoreboard.qualifies(final_score):
                        name_input_screen.reset(final_score)
                        state = "name_input"
                    else:
                        leaderboard_screen.load(highlight_rank=None)
                        state = "leaderboard"

            # ---- NAME INPUT ----
            elif state == "name_input":
                action = name_input_screen.handle_event(event)
                if action == "confirm":
                    rank = scoreboard.save_score(
                        name_input_screen.name,
                        name_input_screen.score,
                    )
                    leaderboard_screen.load(highlight_rank=rank)
                    state = "leaderboard"
                elif action == "skip":
                    leaderboard_screen.load(highlight_rank=None)
                    state = "leaderboard"

            # ---- LEADERBOARD ----
            elif state == "leaderboard":
                action = leaderboard_screen.handle_event(event)
                if action == "menu":
                    state = "menu"

        # ---------------------------------------------------------- #
        # Update (logic)                                              #
        # ---------------------------------------------------------- #
        if state == "game":
            game_screen.update(current_ms, vm)
        elif state == "name_input":
            name_input_screen.update(current_ms)

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
        elif state == "name_input":
            name_input_screen.draw(virtual)
        elif state == "leaderboard":
            leaderboard_screen.draw(virtual)

        blit_virtual(screen, virtual)
        clock.tick(FPS)

    settings.save()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
