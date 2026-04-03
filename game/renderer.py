"""Renderer: Star Wars themed drawing for Terix Galaxy."""
import os
import random
import pygame
from game.tetromino import COLORS

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')
BG_IMAGE_PATH = os.path.join(ASSETS_DIR, 'images', 'background.png')

# -----------------------------------------------------------------------
# Layout constants
# -----------------------------------------------------------------------
CELL = 30
COLS = 10
ROWS = 20
FIELD_X = 50
FIELD_Y = 60
FIELD_W = COLS * CELL
FIELD_H = ROWS * CELL
SIDE_X = FIELD_X + FIELD_W + 30
SCREEN_W = 800
SCREEN_H = 700

# Crawl area (right column for Star Wars perspective text)
CRAWL_X = 510
CRAWL_Y = 60
CRAWL_W = SCREEN_W - CRAWL_X - 10
CRAWL_H = SCREEN_H - CRAWL_Y - 10

# -----------------------------------------------------------------------
# Star Wars color palette — Black & Gold
# -----------------------------------------------------------------------
BG_TOP = (0, 0, 0)                 # Pure space black
BG_BOTTOM = (8, 6, 0)             # Very dark warm black
GRID_LINE = (30, 22, 0)           # Dark gold grid (barely visible)
TEXT_PRIMARY = (255, 240, 180)     # Warm white / parchment
TEXT_ACCENT = (255, 210, 0)        # Star Wars crawl gold
GLOW_COLOR = (255, 210, 0)         # Gold border glow
GHOST_ALPHA = 38                    # ~15% of 255
STAR_COLOR = (220, 210, 180)       # Warm star color

FLASH_DURATION = 10   # frames for galaxy flash

# Star Wars opening crawl story lines
CRAWL_LINES = [
    "A long time ago",
    "in a galaxy",
    "far, far away....",
    "",
    "TERIX  GALAXY",
    "",
    "The galaxy is in chaos.",
    "Tetromino blocks",
    "plunge from the dark",
    "void of space,",
    "threatening to",
    "overwhelm the last",
    "outpost of order.",
    "",
    "The Galactic Council",
    "of Stackers has",
    "fallen. Only one",
    "hero remains.",
    "",
    "Armed with the",
    "wisdom of the Force",
    "and lightning-fast",
    "reflexes, they must",
    "clear the falling",
    "blocks and restore",
    "peace to the galaxy.",
    "",
    "The fate of all",
    "civilizations rests",
    "on a single stack.",
    "",
    "May the blocks",
    "be with you...",
    "",
    "",
    "",
]


class GalaxyCrawl:
    """Star Wars perspective scrolling crawl text."""

    LINE_H = 26
    FONT_SIZE = 15
    SPEED = 0.55   # pixels per frame at 60 fps

    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(
            'Arial', self.FONT_SIZE, bold=True
        )
        self.title_font = pygame.font.SysFont(
            'Arial Black', 18, bold=True
        )
        self._scroll = float(CRAWL_H)
        self._total_h = len(CRAWL_LINES) * self.LINE_H

    def update(self):
        self._scroll -= self.SPEED
        if self._scroll < -self._total_h:
            self._scroll = float(CRAWL_H)

    def draw(self, surface):
        """Draw perspective crawl in the right-side crawl area."""
        clip_rect = pygame.Rect(CRAWL_X, CRAWL_Y, CRAWL_W, CRAWL_H)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        vp_cx = CRAWL_X + CRAWL_W // 2   # vanishing point x

        for i, line in enumerate(CRAWL_LINES):
            # y position from top of crawl area
            y_local = self._scroll + i * self.LINE_H
            if y_local < -self.LINE_H or y_local > CRAWL_H:
                continue

            # Perspective scale: 0 at top (horizon), 1 at bottom
            t = max(0.0, min(1.0, y_local / CRAWL_H))
            scale = t ** 0.62
            if scale < 0.04:
                continue

            text = line or ''
            is_title = (line == 'TERIX  GALAXY')
            f = self.title_font if is_title else self.font
            color = (255, 220, 0) if is_title else (255, 210, 0)

            if not text:
                continue

            raw = f.render(text, True, color)
            new_w = max(1, int(raw.get_width() * scale))
            new_h = max(1, int(raw.get_height() * scale))
            scaled = pygame.transform.smoothscale(raw, (new_w, new_h))

            # Fade out near the top (horizon)
            if t < 0.25:
                alpha = int(255 * (t / 0.25))
                scaled.set_alpha(alpha)

            bx = vp_cx - new_w // 2
            by = CRAWL_Y + int(y_local) - new_h // 2
            surface.blit(scaled, (bx, by))

        surface.set_clip(old_clip)


def _draw_gradient_bg(surface):
    """Draw deep-space gradient background."""
    for y in range(SCREEN_H):
        t = y / SCREEN_H
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_W, y))


def _draw_glow_rect(surface, color, rect, glow_radius=4):
    """Draw a glowing rectangle (lightsaber neon effect)."""
    glow_surf = pygame.Surface(
        (rect.width + glow_radius * 2, rect.height + glow_radius * 2),
        pygame.SRCALPHA
    )
    for i in range(glow_radius, 0, -1):
        alpha = int(90 * (i / glow_radius))
        glow_color = (*color, alpha)
        glow_rect = pygame.Rect(
            glow_radius - i, glow_radius - i,
            rect.width + i * 2, rect.height + i * 2
        )
        pygame.draw.rect(glow_surf, glow_color, glow_rect, border_radius=3)
    surface.blit(glow_surf, (rect.x - glow_radius, rect.y - glow_radius))


def _draw_block(surface, color, col, row, alpha=255, glow=True):
    """Draw a single lightsaber-colored block."""
    x = FIELD_X + col * CELL
    y = FIELD_Y + row * CELL
    rect = pygame.Rect(x + 1, y + 1, CELL - 2, CELL - 2)

    if alpha < 255:
        block_surf = pygame.Surface((CELL - 2, CELL - 2), pygame.SRCALPHA)
        block_surf.fill((*color, alpha))
        surface.blit(block_surf, (x + 1, y + 1))
        return

    if glow:
        _draw_glow_rect(surface, color, rect, glow_radius=5)

    pygame.draw.rect(surface, color, rect, border_radius=2)
    # Bright core line (lightsaber blade effect)
    core = tuple(min(255, c + 100) for c in color)
    inner = pygame.Rect(x + 4, y + 4, CELL - 8, CELL - 8)
    pygame.draw.rect(surface, core, inner, border_radius=1)
    highlight = tuple(min(255, c + 60) for c in color)
    pygame.draw.rect(surface, highlight, rect, width=1, border_radius=2)


def _draw_block_at(surface, color, px, py, size=24):
    """Draw a block at pixel coords (NEXT/HOLD panels)."""
    rect = pygame.Rect(px + 1, py + 1, size - 2, size - 2)
    _draw_glow_rect(surface, color, rect, glow_radius=3)
    pygame.draw.rect(surface, color, rect, border_radius=2)
    core = tuple(min(255, c + 100) for c in color)
    inner = pygame.Rect(px + 4, py + 4, size - 8, size - 8)
    pygame.draw.rect(surface, core, inner, border_radius=1)


def _glow_text(surface, font, text, color, cx, cy):
    """Render text with Star Wars gold glow centered at (cx, cy)."""
    dim = (color[0] // 4, color[1] // 4, color[2] // 4)
    glow_surf = font.render(text, True, dim)
    for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)]:
        r = glow_surf.get_rect(center=(cx + dx, cy + dy))
        surface.blit(glow_surf, r)
    main_surf = font.render(text, True, color)
    r = main_surf.get_rect(center=(cx, cy))
    surface.blit(main_surf, r)


class StarParticle:
    """A single star particle for galaxy line-clear effect."""

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-4, 4)
        self.life = 1.0
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3   # gravity
        self.life -= 0.08

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * self.life)
        c = (*self.color, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, c, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


class Renderer:
    """Handles all Pygame drawing for Terix Galaxy (Star Wars theme)."""

    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font_title = pygame.font.SysFont('Arial Black', 24, bold=True)
        self.font_sub = pygame.font.SysFont('Arial', 11, italic=True)
        self.font_label = pygame.font.SysFont('Arial', 14, bold=True)
        self.font_value = pygame.font.SysFont('Arial Black', 18, bold=True)
        self.font_big = pygame.font.SysFont('Arial Black', 36, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 12)
        # Star field (static background stars)
        self._stars = [
            (random.randint(0, SCREEN_W), random.randint(0, SCREEN_H),
             random.randint(1, 3))
            for _ in range(120)
        ]
        # Galaxy particles for line-clear effect
        self._particles = []
        # Star Wars perspective crawl
        self._crawl = GalaxyCrawl()
        # Load AI-generated background (fallback to gradient+stars)
        self._bg_image = None
        if os.path.exists(BG_IMAGE_PATH):
            try:
                img = pygame.image.load(BG_IMAGE_PATH).convert()
                self._bg_image = pygame.transform.scale(
                    img, (SCREEN_W, SCREEN_H)
                )
            except pygame.error:
                self._bg_image = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw(self, board, current, ghost_y, next_piece, hold_piece,
             paused, game_over, flash_rows=None, flash_frames=0):
        """Main draw call."""
        # Background
        if self._bg_image:
            self.screen.blit(self._bg_image, (0, 0))
        else:
            _draw_gradient_bg(self.screen)
            self._draw_stars()

        self._draw_grid()
        self._draw_stack(board)

        if flash_rows and flash_frames > 0:
            self._draw_galaxy_flash(flash_rows, flash_frames)
        else:
            if ghost_y is not None and current is not None:
                self._draw_ghost(current, ghost_y)
            if current is not None:
                self._draw_piece(current)

        # Update & draw particles
        self._particles = [p for p in self._particles if p.life > 0]
        for p in self._particles:
            p.update()
            p.draw(self.screen)

        self._draw_border()
        self._draw_side_panel(board, next_piece, hold_piece)
        # Separator between stats panel and crawl area
        pygame.draw.line(
            self.screen, (80, 60, 0),
            (CRAWL_X - 8, CRAWL_Y),
            (CRAWL_X - 8, CRAWL_Y + CRAWL_H), 1
        )
        # Star Wars perspective crawl
        self._crawl.update()
        self._crawl.draw(self.screen)
        self._draw_title()

        if paused:
            self._draw_overlay('PAUSED', TEXT_ACCENT)
        if game_over:
            self._draw_overlay('THE FORCE HAS LEFT YOU', (220, 20, 20))

    def spawn_galaxy_particles(self, rows):
        """Spawn Star Wars explosion particles for cleared rows."""
        for row in rows:
            cy = FIELD_Y + row * CELL + CELL // 2
            for col in range(COLS):
                cx = FIELD_X + col * CELL + CELL // 2
                kind_colors = list(COLORS.values())
                color = random.choice(kind_colors)
                for _ in range(4):
                    self._particles.append(StarParticle(cx, cy, color))
            # Add gold sparks
            for _ in range(20):
                cx = random.randint(FIELD_X, FIELD_X + FIELD_W)
                self._particles.append(
                    StarParticle(cx, cy, (255, 210, 50))
                )

    # ------------------------------------------------------------------
    # Static stars
    # ------------------------------------------------------------------

    def _draw_stars(self):
        for (sx, sy, sz) in self._stars:
            b = 140 + sz * 30
            # Warm white / faint gold stars
            c = (b, int(b * 0.95), int(b * 0.75))
            pygame.draw.circle(self.screen, c, (sx, sy), sz)

    # ------------------------------------------------------------------
    # Grid
    # ------------------------------------------------------------------

    def _draw_grid(self):
        for col in range(COLS + 1):
            x = FIELD_X + col * CELL
            pygame.draw.line(self.screen, GRID_LINE,
                             (x, FIELD_Y), (x, FIELD_Y + FIELD_H))
        for row in range(ROWS + 1):
            y = FIELD_Y + row * CELL
            pygame.draw.line(self.screen, GRID_LINE,
                             (FIELD_X, y), (FIELD_X + FIELD_W, y))

    def _draw_border(self):
        """Gold border (Imperial/Republic gold)."""
        rect = pygame.Rect(FIELD_X - 2, FIELD_Y - 2,
                           FIELD_W + 4, FIELD_H + 4)
        pygame.draw.rect(self.screen, GLOW_COLOR, rect, width=2,
                         border_radius=4)
        # Double border for Star Wars feel
        rect2 = pygame.Rect(FIELD_X - 4, FIELD_Y - 4,
                            FIELD_W + 8, FIELD_H + 8)
        dim_gold = (120, 90, 10)
        pygame.draw.rect(self.screen, dim_gold, rect2, width=1,
                         border_radius=5)

    # ------------------------------------------------------------------
    # Stack & pieces
    # ------------------------------------------------------------------

    def _draw_stack(self, board):
        for row in range(ROWS):
            for col in range(COLS):
                kind = board.grid[row][col]
                if kind:
                    _draw_block(self.screen, COLORS[kind], col, row)

    def _draw_piece(self, piece):
        color = COLORS[piece.kind]
        for (col, row) in piece.get_cells():
            if row >= 0:
                _draw_block(self.screen, color, col, row)

    def _draw_ghost(self, piece, ghost_y):
        color = COLORS[piece.kind]
        ghost = piece.clone()
        ghost.y = ghost_y
        for (col, row) in ghost.get_cells():
            if row >= 0:
                _draw_block(self.screen, color, col, row,
                            alpha=GHOST_ALPHA, glow=False)

    # ------------------------------------------------------------------
    # Galaxy line-clear flash effect
    # ------------------------------------------------------------------

    def _draw_galaxy_flash(self, rows, flash_frames):
        """Lightsaber sweep + hyperspace flash on cleared rows."""
        progress = 1.0 - (flash_frames / FLASH_DURATION)

        for row in rows:
            y = FIELD_Y + row * CELL
            # Sweeping lightsaber beam across the row
            sweep_x = int(FIELD_X + FIELD_W * progress)
            beam_surf = pygame.Surface((FIELD_W, CELL), pygame.SRCALPHA)

            # White core beam
            alpha_beam = int(220 * (1.0 - progress * 0.5))
            beam_surf.fill((255, 255, 255, alpha_beam))
            self.screen.blit(beam_surf, (FIELD_X, y))

            # Gold/cyan energy color overlay
            energy_color = (
                int(255 * (1 - progress)),
                int(200 * (1 - progress * 0.5)),
                int(50 + 200 * progress)
            )
            energy_surf = pygame.Surface((sweep_x - FIELD_X, CELL),
                                         pygame.SRCALPHA)
            energy_surf.fill((*energy_color, 120))
            self.screen.blit(energy_surf, (FIELD_X, y))

            # Horizontal glow line (lightsaber blade)
            cy = y + CELL // 2
            for thickness, al in [(6, 40), (3, 80), (1, 200)]:
                blade_surf = pygame.Surface((FIELD_W, thickness * 2),
                                            pygame.SRCALPHA)
                blade_surf.fill((200, 220, 255, al))
                self.screen.blit(blade_surf,
                                 (FIELD_X, cy - thickness))

        # Star burst at center of cleared rows
        if flash_frames > FLASH_DURATION // 2:
            mid_row = rows[len(rows) // 2]
            cy = FIELD_Y + mid_row * CELL + CELL // 2
            burst_r = int(FIELD_W * 0.4 * progress)
            burst_surf = pygame.Surface(
                (burst_r * 2 + 4, burst_r * 2 + 4), pygame.SRCALPHA
            )
            alpha_burst = int(180 * (1.0 - progress))
            center = (burst_r + 2, burst_r + 2)
            pygame.draw.circle(burst_surf, (255, 240, 180, alpha_burst),
                               center, burst_r)
            self.screen.blit(burst_surf,
                             (FIELD_X + FIELD_W // 2 - burst_r - 2,
                              cy - burst_r - 2))

    # ------------------------------------------------------------------
    # Title & side panel
    # ------------------------------------------------------------------

    def _draw_title(self):
        _glow_text(self.screen, self.font_title, 'TERIX  GALAXY',
                   TEXT_ACCENT, FIELD_X + FIELD_W // 2, 28)
        sub = self.font_sub.render(
            '* May the blocks be with you *', True, (200, 170, 0)
        )
        r = sub.get_rect(center=(FIELD_X + FIELD_W // 2, 47))
        self.screen.blit(sub, r)

    def _draw_side_panel(self, board, next_piece, hold_piece):
        sx = SIDE_X
        self._draw_stat(sx, 70, 'SCORE', str(board.score))
        self._draw_stat(sx, 130, 'LEVEL', str(board.level))
        self._draw_stat(sx, 190, 'LINES', str(board.lines_cleared))
        self._draw_panel_label(sx, 260, 'NEXT')
        if next_piece:
            self._draw_mini_piece(next_piece, sx, 285)
        self._draw_panel_label(sx, 390, 'HOLD')
        if hold_piece:
            self._draw_mini_piece(hold_piece, sx, 415)
        hints = [
            '\u2190 \u2192 move', '\u2191 rotate',
            '\u2193 soft drop', 'SPC hard drop',
            'C hold', 'P pause', 'R restart'
        ]
        for i, hint in enumerate(hints):
            txt = self.font_small.render(hint, True, (180, 150, 0))
            self.screen.blit(txt, (sx, 560 + i * 17))

    def _draw_stat(self, x, y, label, value):
        lbl = self.font_label.render(label, True, TEXT_ACCENT)
        self.screen.blit(lbl, (x, y))
        _glow_text(self.screen, self.font_value, value,
                   TEXT_PRIMARY, x + 60, y + 22)

    def _draw_panel_label(self, x, y, text):
        lbl = self.font_label.render(text, True, TEXT_ACCENT)
        self.screen.blit(lbl, (x, y))
        pygame.draw.line(self.screen, GLOW_COLOR,
                         (x, y + 18), (x + 110, y + 18), 1)

    def _draw_mini_piece(self, piece, px, py):
        size = 24
        color = COLORS[piece.kind]
        offsets = piece.get_cells()
        min_col = min(c for c, r in offsets)
        min_row = min(r for c, r in offsets)
        for (col, row) in offsets:
            bx = px + (col - min_col) * size
            by = py + (row - min_row) * size
            _draw_block_at(self.screen, color, bx, by, size)

    # ------------------------------------------------------------------
    # Overlay
    # ------------------------------------------------------------------

    def _draw_overlay(self, text, color):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))
        # Draw text — shrink font if text is long
        if len(text) > 12:
            font = pygame.font.SysFont('Arial Black', 24, bold=True)
        else:
            font = self.font_big
        _glow_text(self.screen, font, text,
                   color, SCREEN_W // 2, SCREEN_H // 2 - 20)
        hint = self.font_label.render(
            'Press R to restart  |  ESC to quit',
            True, TEXT_PRIMARY
        )
        r = hint.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30))
        self.screen.blit(hint, r)
