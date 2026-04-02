import sys
import os
import pygame
from settings import Settings

# Virtual canvas — all game logic uses this fixed resolution
VIRTUAL_W = 800
VIRTUAL_H = 600
TITLE = "KacasBrickBreaker"
FPS = 60


def make_screen(fullscreen: bool) -> pygame.Surface:
    """Create and return the real pygame display surface."""
    if fullscreen:
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return pygame.display.set_mode((VIRTUAL_W, VIRTUAL_H))


def ensure_scores_dir():
    """Make sure scores/ folder and highscore.txt exist."""
    os.makedirs("scores", exist_ok=True)
    path = os.path.join("scores", "highscore.txt")
    if not os.path.exists(path):
        open(path, "w").close()


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    settings = Settings()
    settings.load()

    ensure_scores_dir()

    screen = make_screen(settings.fullscreen)
    # Virtual surface — everything is drawn here, then scaled to screen
    virtual = pygame.Surface((VIRTUAL_W, VIRTUAL_H))

    clock = pygame.time.Clock()

    # ------------------------------------------------------------------ #
    # Placeholder game loop — will be replaced by the state machine       #
    # in Phase 2 when menu.py / game.py are introduced                    #
    # ------------------------------------------------------------------ #
    font = pygame.font.SysFont("Courier", 28, bold=True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_F11:
                    # Toggle fullscreen
                    settings.fullscreen = not settings.fullscreen
                    settings.save()
                    screen = make_screen(settings.fullscreen)

        # Draw to virtual surface
        virtual.fill((10, 14, 42))  # Dark navy #0A0E2A
        msg = font.render("Phase 1 OK — press ESC to quit, F11 = fullscreen", True, (255, 255, 255))
        virtual.blit(msg, (VIRTUAL_W // 2 - msg.get_width() // 2, VIRTUAL_H // 2 - msg.get_height() // 2))

        # Scale virtual surface to real screen and present
        real_w, real_h = screen.get_size()
        if (real_w, real_h) == (VIRTUAL_W, VIRTUAL_H):
            screen.blit(virtual, (0, 0))
        else:
            scaled = pygame.transform.scale(virtual, (real_w, real_h))
            screen.blit(scaled, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    settings.save()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
