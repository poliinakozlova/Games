# точка входу: python main.py
import os

from settings import SND_DIR
from sounds import SOUND_FILES, MUSIC_FILE


def main():
    # звуки генеруються pydub при першому запуску
    files = list(SOUND_FILES.values()) + [MUSIC_FILE]
    if not all(os.path.exists(os.path.join(SND_DIR, f)) for f in files):
        import make_sounds
        make_sounds.generate_all()

    from game import Game
    Game().run()


if __name__ == "__main__":
    main()
