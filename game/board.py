"""Game board: grid state, collision, line clear, score."""
import random
from game.tetromino import Tetromino

SCORE_TABLE = {1: 100, 2: 300, 3: 500, 4: 800}


class Board:
    """Represents the 10x20 Tetrix game board."""

    WIDTH = 10
    HEIGHT = 20

    def __init__(self):
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.reset()

    def reset(self):
        """Reset board to initial state."""
        self.grid = [[None] * self.width for _ in range(self.height)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False

    # ------------------------------------------------------------------
    # Collision detection
    # ------------------------------------------------------------------

    def is_valid(self, piece):
        """Return True if piece position has no collision."""
        for (col, row) in piece.get_cells():
            if col < 0 or col >= self.width:
                return False
            if row >= self.height:
                return False
            if row >= 0 and self.grid[row][col] is not None:
                return False
        return True

    # ------------------------------------------------------------------
    # Locking
    # ------------------------------------------------------------------

    def lock_piece(self, piece):
        """Lock piece into grid. Sets game_over if any cell is above row 0."""
        for (col, row) in piece.get_cells():
            if row < 0:
                self.game_over = True
                return
            if row < self.height:
                self.grid[row][col] = piece.kind
        # Check if any locked cell is in row 0 (top row visible)
        # Game over if a piece stacks into the spawn area
        for col in range(self.width):
            if self.grid[0][col] is not None:
                pass  # will be caught next spawn attempt

    # ------------------------------------------------------------------
    # Line clearing
    # ------------------------------------------------------------------

    def clear_lines(self):
        """Remove full rows, drop above. Return number of lines cleared."""
        remaining_rows = [
            row for row in self.grid
            if any(cell is None for cell in row)
        ]
        count = self.height - len(remaining_rows)
        if count == 0:
            return 0

        self.grid = [[None] * self.width for _ in range(count)] + remaining_rows
        self.lines_cleared += count
        new_level = self.lines_cleared // 10 + 1
        self.level = new_level
        self.add_score(count)
        return count

    # ------------------------------------------------------------------
    # Score
    # ------------------------------------------------------------------

    def add_score(self, lines):
        """Add score for cleared lines (already level-multiplied)."""
        base = SCORE_TABLE.get(lines, 0)
        self.score += base * self.level

    # ------------------------------------------------------------------
    # Hard drop helper
    # ------------------------------------------------------------------

    def hard_drop_y(self, piece):
        """Return the lowest valid Y position for piece (ghost/hard drop)."""
        test = piece.clone()
        while True:
            test.y += 1
            if not self.is_valid(test):
                return test.y - 1

    # ------------------------------------------------------------------
    # Fall speed
    # ------------------------------------------------------------------

    def fall_interval_ms(self):
        """Return fall interval in ms based on current level."""
        base = 800
        reduction = (self.level - 1) * 60
        return max(80, base - reduction)

    # ------------------------------------------------------------------
    # Test helper
    # ------------------------------------------------------------------

    def _fill_row_for_test(self):
        """Fill the bottom-most non-full row for test_score level-up test."""
        for r in range(self.height - 1, -1, -1):
            if any(self.grid[r][c] is None for c in range(self.width)):
                for c in range(self.width):
                    self.grid[r][c] = 'I'
                return

    # ------------------------------------------------------------------
    # Spawn check
    # ------------------------------------------------------------------

    def check_spawn(self, piece):
        """Return False (game over) if piece overlaps existing stack."""
        if not self.is_valid(piece):
            self.game_over = True
            return False
        return True

    # ------------------------------------------------------------------
    # Random piece factory
    # ------------------------------------------------------------------

    @staticmethod
    def random_piece():
        kinds = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
        return Tetromino(random.choice(kinds))
