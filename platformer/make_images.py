# зберігає намальовані картинки в images/
import os

import pygame

from assets import FALLBACKS, SIZES
from settings import IMG_DIR


def main():
    pygame.init()
    os.makedirs(IMG_DIR, exist_ok=True)
    for name, size in SIZES.items():
        path = os.path.join(IMG_DIR, name + ".png")
        if not os.path.exists(path):
            pygame.image.save(FALLBACKS[name](size), path)
            print("створено", path, size)


if __name__ == "__main__":
    main()
