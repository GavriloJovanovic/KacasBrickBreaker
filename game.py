"""
Game — owns one full play session.

Internal states:
  "waiting"   — ball sitting on paddle, waiting for launch input
  "playing"   — active gameplay
  "paused"    — ESC pressed mid-game; overlay shown
  "game_over" — lives exhausted or bricks reached paddle

handle_event() returns:
  "menu"      — leave game, go back to main menu
  "game_over" — game ended; main.py reads self.score then transitions
  None        — no state change for main.py
"""
import pygame

from ball         import Ball
from paddle       import Paddle
from brick        import Brick
from brick_manager import BrickManager
from hud          import HUD
from ui           import draw_text_centered, make_overlay

VIRTUAL_W  = 800
VIRTUAL_H  = 600
MAX_LIVES  = 3
BASE_SPEED = 5.0     # ball speed at level 1 (px / frame)
MAX_SPEED  = 15.0    # hard cap so the game stays playable

# How many bricks broken to reach each level
LEVEL_THRESHOLD = 20

LEVELUP_DISPLAY_MS = 2000   # how long the "LEVEL UP" banner stays on screen

_OVERLAY_DARK = (0, 0, 0, 160)   # SRCALPHA overlay colour

_WHITE  = (255, 255, 255)
_YELLOW = (255, 220,  50)
_RED    = (220,  50,  50)
_DIM    = ( 80,  90, 130)


class Game:
    def __init__(self, settings, bg: pygame.Surface):
        self.settings = settings
        self.bg       = bg

        # Game objects — created once, reset on new_game()
        self.ball          = Ball()
        self.paddle        = Paddle(settings)
        self.brick_manager = BrickManager()
        self.hud           = HUD()

        # Game state
        self.score         = 0
        self.level         = 1
        self.lives         = MAX_LIVES
        self.bricks_broken = 0
        self._state        = "waiting"

        # Level-up banner timer (pygame ticks)
        self._levelup_until: int = 0

        # Fonts (lazy — only created after pygame.init() is confirmed)
        self._fonts: dict | None = None

    # ================================================================== #
    # Public API called by main.py                                        #
    # ================================================================== #

    def new_game(self, current_ms: int):
        """Reset everything and start a fresh game."""
        self.score         = 0
        self.level         = 1
        self.lives         = MAX_LIVES
        self.bricks_broken = 0
        self._state        = "waiting"
        self._levelup_until = 0

        self.ball.set_speed(BASE_SPEED)
        self.brick_manager.start(current_ms)
        self._sync_ball_to_paddle()

    # ------------------------------------------------------------------ #

    def handle_event(self, event, virt_mouse) -> str | None:
        """
        Process one pygame event.
        Returns "menu" or "game_over", or None if no transition needed.
        """
        fonts = self._get_fonts()

        # ---- GAME OVER screen — any key / click exits ----
        if self._state == "game_over":
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return "game_over"
            return None

        # ---- PAUSED ----
        if self._state == "paused":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._state = "playing"     # ESC resumes
                elif event.key == pygame.K_m:
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Click the "MAIN MENU" area (rough check)
                mx, my = virt_mouse
                if 300 <= mx <= 500 and 340 <= my <= 390:
                    return "menu"
            return None

        # ---- PLAYING / WAITING ----
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self._state in ("playing", "waiting"):
                    self._state = "paused"

            elif event.key == pygame.K_SPACE:
                if self._state == "waiting":
                    self._launch()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._state == "waiting":
                self._launch()

        return None

    # ------------------------------------------------------------------ #

    def update(self, current_ms: int, virt_mouse):
        """Run one frame of game logic. Called every frame by main.py."""
        if self._state not in ("playing", "waiting"):
            return

        # Always update paddle
        self.paddle.update(virt_mouse)

        if self._state == "waiting":
            self._sync_ball_to_paddle()
            return

        # --- Move ball ---
        result = self.ball.update()

        if result == "bottom":
            self._handle_life_lost()
            return

        # --- Ball vs paddle (only when ball is moving downward) ---
        if self.ball.dy > 0 and self.ball.rect.colliderect(self.paddle.rect):
            self.ball.bounce_off_paddle(self.paddle.rect)

        # --- Ball vs bricks ---
        destroyed = self.brick_manager.collide_ball(self.ball)
        if destroyed:
            self.score         += destroyed * 10
            self.bricks_broken += destroyed
            self._check_level_up(current_ms)

        # --- Brick spawn timer ---
        self.brick_manager.update(self.level, current_ms)

        # --- Danger: bricks reached the paddle zone ---
        if self.brick_manager.check_danger():
            self._state = "game_over"

    # ------------------------------------------------------------------ #

    def draw(self, surface: pygame.Surface, virt_mouse):
        """Draw the complete game frame onto surface."""
        # Background
        surface.blit(self.bg, (0, 0))

        # Game objects
        self.brick_manager.draw(surface)
        self.paddle.draw(surface)
        self.ball.draw(surface)

        # HUD
        self.hud.draw(surface, self.score, self.level, self.lives, MAX_LIVES)

        # Level-up banner
        if pygame.time.get_ticks() < self._levelup_until:
            self._draw_levelup_banner(surface)

        # State overlays
        if self._state == "waiting":
            self._draw_launch_hint(surface)
        elif self._state == "paused":
            self._draw_pause(surface)
        elif self._state == "game_over":
            self._draw_game_over(surface)

    # ================================================================== #
    # Internal helpers                                                    #
    # ================================================================== #

    def _launch(self):
        self.ball.launch()
        self._state = "playing"

    def _sync_ball_to_paddle(self):
        """Keep the idle ball centred on top of the paddle."""
        pr = self.paddle.rect
        self.ball.x = float(pr.centerx)
        self.ball.y = float(pr.y - Ball.RADIUS - 1)

    def _handle_life_lost(self):
        self.lives -= 1
        if self.lives <= 0:
            self._state = "game_over"
        else:
            self._sync_ball_to_paddle()
            self._state = "waiting"

    def _check_level_up(self, current_ms: int):
        new_level = 1 + self.bricks_broken // LEVEL_THRESHOLD
        if new_level > self.level:
            self.level  = new_level
            self.score += 100 * new_level           # level bonus
            new_speed   = BASE_SPEED + (new_level - 1) * 1.0
            self.ball.set_speed(min(MAX_SPEED, new_speed))
            self._levelup_until = current_ms + LEVELUP_DISPLAY_MS

    # ================================================================== #
    # Overlay / banner drawing                                            #
    # ================================================================== #

    def _get_fonts(self) -> dict:
        if self._fonts is None:
            self._fonts = {
                "big":    pygame.font.SysFont("Courier New", 52, bold=True),
                "medium": pygame.font.SysFont("Courier New", 28, bold=True),
                "small":  pygame.font.SysFont("Courier New", 18, bold=False),
                "hint":   pygame.font.SysFont("Courier New", 16, bold=False),
            }
        return self._fonts

    def _draw_launch_hint(self, surface: pygame.Surface):
        f = self._get_fonts()
        draw_text_centered(surface,
                           "PRESS  SPACE  OR  CLICK  TO  LAUNCH",
                           f["hint"], (180, 200, 255),
                           VIRTUAL_H - 80, shadow=True)

    def _draw_levelup_banner(self, surface: pygame.Surface):
        f   = self._get_fonts()
        ov  = make_overlay(VIRTUAL_W, 70, alpha=170)
        surface.blit(ov, (0, VIRTUAL_H // 2 - 35))
        draw_text_centered(surface, f"LEVEL  UP!   NOW  LEVEL  {self.level}",
                           f["medium"], _YELLOW, VIRTUAL_H // 2 - 14, shadow=True)

    def _draw_pause(self, surface: pygame.Surface):
        f  = self._get_fonts()
        ov = make_overlay(VIRTUAL_W, VIRTUAL_H, alpha=170)
        surface.blit(ov, (0, 0))

        draw_text_centered(surface, "PAUSED",   f["big"],    _WHITE,  200, shadow=True)
        draw_text_centered(surface, "ESC — RESUME",         f["small"], _DIM,   300)
        draw_text_centered(surface, "M — MAIN MENU",        f["small"], _DIM,   330)

    def _draw_game_over(self, surface: pygame.Surface):
        f  = self._get_fonts()
        ov = make_overlay(VIRTUAL_W, VIRTUAL_H, alpha=180)
        surface.blit(ov, (0, 0))

        draw_text_centered(surface, "GAME  OVER",           f["big"],    _RED,    185, shadow=True)
        draw_text_centered(surface, f"SCORE:  {self.score:06d}", f["medium"], _WHITE,  270)
        draw_text_centered(surface, f"LEVEL  REACHED:  {self.level}", f["small"],  _DIM, 320)
        draw_text_centered(surface, "PRESS  ANY  KEY  TO  CONTINUE", f["hint"], _DIM,   390)
