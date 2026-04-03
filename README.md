# tetrix_galaxy
Star Wars-inspired 2D Tetris game built with Pygame.

## What is included

This repository is trimmed for players/users:
- Runtime source code in `main.py` and `game/`
- Required game assets in `assets/`
- Runtime dependency list in `requirements.txt`

Development-only materials are kept out of GitHub upload via `.gitignore` (`dev_only/`).

## Requirements

- Python 3.10+
- macOS / Windows / Linux

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the game:

```bash
python main.py
```

## Controls

- Left / Right: Move block
- Up: Rotate clockwise
- Down: Soft drop
- Space: Hard drop
- C: Hold piece
- P: Pause / Resume
- R: Restart
- ESC: Exit

## Project Structure (public)

```text
main.py
requirements.txt
README.md
assets/
  images/
  sounds/
game/
  audio.py
  board.py
  renderer.py
  tetromino.py
```
