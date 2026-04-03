"""Tetromino definitions, rotation, and wall kick data."""

# Lightsaber color palette (Star Wars)
COLORS = {
    'I': (0, 150, 255),    # Blue  (Obi-Wan / Anakin)
    'O': (255, 210, 0),    # Gold  (Luke / Republic)
    'T': (180, 0, 255),    # Purple (Mace Windu)
    'S': (0, 220, 80),     # Green (Yoda)
    'Z': (220, 20, 20),    # Red   (Sith)
    'J': (0, 200, 240),    # Cyan  (lightsaber glow)
    'L': (255, 100, 0),    # Orange (Ahsoka)
}

# Each piece has 4 rotations; each rotation is a list of (col, row) offsets
SHAPES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

# SRS wall kick offsets: key is (from_rotation, to_rotation)
WALL_KICKS = {
    'normal': {
        (0, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (1, 0): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        (1, 2): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        (2, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (2, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (3, 2): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (3, 0): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (0, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
    },
    'I': {
        (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],
        (1, 0): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],
        (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],
        (2, 1): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],
        (2, 3): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],
        (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],
        (3, 0): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],
        (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],
    },
}


class Tetromino:
    """A single tetromino piece."""

    def __init__(self, kind):
        self.kind = kind
        self.rotation = 0
        self.x = 3   # spawn column
        self.y = 0   # spawn row

    def get_cells(self):
        """Return absolute (col, row) positions of all 4 cells."""
        offsets = SHAPES[self.kind][self.rotation]
        return [(self.x + dx, self.y + dy) for dx, dy in offsets]

    def rotate_cw(self):
        """Rotate clockwise (increment rotation index)."""
        self.rotation = (self.rotation + 1) % 4

    def rotate_ccw(self):
        """Rotate counter-clockwise."""
        self.rotation = (self.rotation - 1) % 4

    def clone(self):
        """Return an independent copy of this piece."""
        t = Tetromino(self.kind)
        t.rotation = self.rotation
        t.x = self.x
        t.y = self.y
        return t
