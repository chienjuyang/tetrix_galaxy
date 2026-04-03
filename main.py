"""Terix Galaxy — main game loop (Star Wars theme)."""
import sys
import random
import pygame

from game.board import Board
from game.tetromino import Tetromino, WALL_KICKS
from game.renderer import Renderer, SCREEN_W, SCREEN_H
from game.audio import Audio

FPS = 60
FLASH_DURATION = 10   # frames for galaxy line-clear flash

# DAS / ARR key-repeat constants (ms)
DAS_DELAY = 170
ARR_INTERVAL = 50


def _new_piece():
    kinds = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
    return Tetromino(random.choice(kinds))


def _try_rotate(board, piece, cw=True):
    """Attempt SRS rotation with wall kicks. Returns True if rotated."""
    from_rot = piece.rotation
    if cw:
        piece.rotate_cw()
    else:
        piece.rotate_ccw()
    to_rot = piece.rotation

    table_key = 'I' if piece.kind == 'I' else 'normal'
    kicks = WALL_KICKS[table_key].get((from_rot, to_rot), [(0, 0)])

    for (ox, oy) in kicks:
        piece.x += ox
        piece.y -= oy   # SRS y-axis is inverted vs screen
        if board.is_valid(piece):
            return True
        piece.x -= ox
        piece.y += oy

    # Revert rotation
    if cw:
        piece.rotate_ccw()
    else:
        piece.rotate_cw()
    return False


class Game:
    """Main game state machine."""

    def __init__(self, screen, audio):
        self.screen = screen
        self.audio = audio
        self.renderer = Renderer(screen)
        self._init_state()

    def _init_state(self):
        self.board = Board()
        self.current = _new_piece()
        self.next_piece = _new_piece()
        self.hold = None
        self.hold_used = False   # can only hold once per piece
        self.paused = False
        self.flash_rows = []
        self.flash_frames = 0
        self.fall_timer = 0
        self.lock_delay = 0
        self.lock_delay_max = 500   # ms
        self.on_ground = False
        # DAS state
        self.das_left = 0
        self.das_right = 0
        self.arr_left = 0
        self.arr_right = 0
        self.audio.play_bgm()

    def restart(self):
        self.audio.stop_bgm()
        self._init_state()

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._on_keydown(event.key)

    def _on_keydown(self, key):
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if key == pygame.K_r:
            self.restart()
            return

        if key == pygame.K_p:
            self.paused = not self.paused
            return

        if self.paused or self.board.game_over:
            return

        if key == pygame.K_UP or key == pygame.K_z:
            if _try_rotate(self.board, self.current, cw=True):
                self.audio.play('rotate')
                self._update_ground()

        if key == pygame.K_DOWN:
            self._soft_drop()

        if key == pygame.K_SPACE:
            self._hard_drop()

        if key == pygame.K_c:
            self._do_hold()

    def _handle_das(self, dt):
        """Handle DAS/ARR for left/right movement."""
        keys = pygame.key.get_pressed()
        moved = False

        if keys[pygame.K_LEFT]:
            if self.das_left == 0:
                if self._move(-1):
                    moved = True
            self.das_left += dt
            if self.das_left >= DAS_DELAY:
                self.arr_left += dt
                while self.arr_left >= ARR_INTERVAL:
                    self.arr_left -= ARR_INTERVAL
                    if self._move(-1):
                        moved = True
        else:
            self.das_left = 0
            self.arr_left = 0

        if keys[pygame.K_RIGHT]:
            if self.das_right == 0:
                if self._move(1):
                    moved = True
            self.das_right += dt
            if self.das_right >= DAS_DELAY:
                self.arr_right += dt
                while self.arr_right >= ARR_INTERVAL:
                    self.arr_right -= ARR_INTERVAL
                    if self._move(1):
                        moved = True
        else:
            self.das_right = 0
            self.arr_right = 0

        if moved:
            self.audio.play('move')
            self._update_ground()

    def _move(self, dx):
        self.current.x += dx
        if self.board.is_valid(self.current):
            return True
        self.current.x -= dx
        return False

    def _soft_drop(self):
        self.current.y += 1
        if not self.board.is_valid(self.current):
            self.current.y -= 1
            self._lock_piece()
        else:
            self.fall_timer = 0

    def _hard_drop(self):
        drop_y = self.board.hard_drop_y(self.current)
        self.current.y = drop_y
        self.audio.play('drop')
        self._lock_piece()

    def _do_hold(self):
        if self.hold_used:
            return
        self.hold_used = True
        if self.hold is None:
            self.hold = Tetromino(self.current.kind)
            self._spawn_next()
        else:
            self.hold, self.current = (
                Tetromino(self.current.kind),
                Tetromino(self.hold.kind)
            )
            self.current.x = 3
            self.current.y = 0
            if not self.board.check_spawn(self.current):
                return

    # ------------------------------------------------------------------
    # Piece lifecycle
    # ------------------------------------------------------------------

    def _update_ground(self):
        test = self.current.clone()
        test.y += 1
        self.on_ground = not self.board.is_valid(test)

    def _lock_piece(self):
        self.board.lock_piece(self.current)
        if self.board.game_over:
            self.audio.play('gameover')
            return
        # Check line clear
        filled = [
            r for r in range(self.board.height)
            if all(self.board.grid[r][c] is not None
                   for c in range(self.board.width))
        ]
        if filled:
            self.flash_rows = filled
            self.flash_frames = FLASH_DURATION
            # Spawn galaxy explosion particles
            self.renderer.spawn_galaxy_particles(filled)
        else:
            self._do_clear_and_spawn()

    def _do_clear_and_spawn(self):
        lines = self.board.clear_lines()
        if lines == 4:
            self.audio.play('tetris')
        elif lines > 0:
            self.audio.play('clear')
        self._spawn_next()

    def _spawn_next(self):
        self.current = self.next_piece
        self.next_piece = _new_piece()
        self.hold_used = False
        self.fall_timer = 0
        self.lock_delay = 0
        self.on_ground = False
        if not self.board.check_spawn(self.current):
            self.audio.play('gameover')

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt):
        if self.paused or self.board.game_over:
            return

        # Flash animation
        if self.flash_frames > 0:
            self.flash_frames -= 1
            if self.flash_frames == 0:
                self._do_clear_and_spawn()
                self.flash_rows = []
            return

        self._handle_das(dt)
        self._update_ground()

        # Gravity
        interval = self.board.fall_interval_ms()
        self.fall_timer += dt
        if self.fall_timer >= interval:
            self.fall_timer -= interval
            self.current.y += 1
            if not self.board.is_valid(self.current):
                self.current.y -= 1
                # Lock delay
                self.lock_delay += dt
                if self.lock_delay >= self.lock_delay_max:
                    self._lock_piece()
                    self.lock_delay = 0
            else:
                self.lock_delay = 0

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self):
        ghost_y = None
        if not self.board.game_over and not self.paused:
            ghost_y = self.board.hard_drop_y(self.current)
        self.renderer.draw(
            board=self.board,
            current=self.current,
            ghost_y=ghost_y,
            next_piece=self.next_piece,
            hold_piece=self.hold,
            paused=self.paused,
            game_over=self.board.game_over,
            flash_rows=self.flash_rows,
            flash_frames=self.flash_frames,
        )


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Terix Galaxy')
    clock = pygame.time.Clock()
    audio = Audio()
    game = Game(screen, audio)

    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.update(dt)
        game.draw()
        pygame.display.flip()


if __name__ == '__main__':
    main()
