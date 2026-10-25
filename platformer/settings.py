# налаштування гри
import os

# вікно
WIDTH, HEIGHT = 960, 600
FPS = 60
TITLE = "Платформер"
TILE = 40                      # розмір клітинки

# шляхи
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "images")
SND_DIR = os.path.join(BASE_DIR, "sounds")
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")

# фізика
GRAVITY = 0.8                  # гравітація
MAX_FALL = 16                  # макс. швидкість падіння
PLAYER_SPEED = 5
JUMP_POWER = 15                # сила стрибка
JUMP_CUT = 4                   # короткий стрибок
STOMP_BOUNCE = 10              # відскок від ворога
ENEMY_SPEED = 1.3              # маршмелоу
CUPCAKE_SPEED = 1.9            # кексик швидший
PLATFORM_SPEED = 2             # рухомі платформи
INVULNERABLE_FRAMES = 90       # невразливість після удару

# гра
START_LIVES = 3
COIN_SCORE = 10
ENEMY_SCORE = 50
LEVEL_COMPLETE_DELAY = 120     # пауза після фінішу

# кольори rgb
WHITE = (255, 255, 255)
SHADOW = (45, 20, 75)
PINK = (255, 175, 225)
LAVENDER = (215, 190, 255)
OVERLAY = (30, 10, 55, 160)
BUTTON_COLOR = (115, 70, 175)
BUTTON_HOVER = (255, 125, 195)
BUTTON_BORDER = (45, 20, 75)
