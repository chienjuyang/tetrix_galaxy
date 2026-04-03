"""Audio manager: sound effects and BGM (gracefully optional)."""
import os
import pygame


class Audio:
    """Manages game sounds. Fails silently if pygame.mixer is unavailable."""

    def __init__(self):
        self._enabled = False
        self._sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16,
                                  channels=2, buffer=512)
            self._enabled = True
        except pygame.error:
            pass
        self._load_sounds()

    def _load_sounds(self):
        sound_dir = os.path.join(
            os.path.dirname(__file__), '..', 'assets', 'sounds'
        )
        mapping = {
            'move': 'move.wav',
            'rotate': 'rotate.wav',
            'drop': 'drop.wav',
            'clear': 'clear.wav',
            'tetris': 'tetris.wav',
            'levelup': 'levelup.wav',
            'gameover': 'gameover.wav',
        }
        if not self._enabled:
            return
        for key, filename in mapping.items():
            path = os.path.join(sound_dir, filename)
            if os.path.exists(path):
                try:
                    self._sounds[key] = pygame.mixer.Sound(path)
                except pygame.error:
                    pass

    def play(self, name):
        if not self._enabled:
            return
        sound = self._sounds.get(name)
        if sound:
            sound.play()

    def play_bgm(self, filename='bgm.mp3'):
        if not self._enabled:
            return
        path = os.path.join(
            os.path.dirname(__file__), '..', 'assets', 'sounds', filename
        )
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass

    def stop_bgm(self):
        if self._enabled:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass
