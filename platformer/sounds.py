# звуки і музика
import os

import pygame

from settings import SND_DIR

# назва -> файл у sounds/
SOUND_FILES = {
    "jump": "jump.wav",
    "coin": "coin.wav",
    "stomp": "stomp.wav",
    "hurt": "hurt.wav",
    "level_complete": "level_complete.wav",
    "game_over": "game_over.wav",
    "click": "click.wav",
}
MUSIC_FILE = "music.wav"


class SoundManager:
    def __init__(self, volume=0.5):
        self.sounds = {}
        self.enabled = pygame.mixer.get_init() is not None   # без звукової карти - тиша
        if not self.enabled:
            return
        for name, filename in SOUND_FILES.items():
            path = os.path.join(SND_DIR, filename)
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                self.sounds[name] = sound

    def play(self, name):
        # програти звук
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def play_music(self):
        path = os.path.join(SND_DIR, MUSIC_FILE)
        if self.enabled and os.path.exists(path) and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)       # -1 = зациклити

    def stop_music(self):
        if self.enabled:
            pygame.mixer.music.stop()
