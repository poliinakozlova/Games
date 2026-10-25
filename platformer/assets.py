# картинки гри (піксель-арт)
import math
import random

import os
import pygame

from settings import IMG_DIR, TILE, WIDTH, HEIGHT

PIXEL = 2      # 1 піксель арту = 2x2 на екрані

# ім'я файлу -> розмір у грі
SIZES = {
    "player_idle": (32, 44),
    "player_run_1": (32, 44),
    "player_run_2": (32, 44),
    "player_jump": (32, 44),
    "marshmallow_1": (36, 30),
    "marshmallow_2": (36, 30),
    "cupcake_1": (36, 30),
    "cupcake_2": (36, 30),
    "coin": (24, 24),
    "ground_top": (TILE, TILE),
    "ground": (TILE, TILE),
    "platform": (TILE, 20),
    "moving_platform": (TILE, 20),
    "spike": (TILE, 20),
    "flag": (TILE, TILE * 2),
    "heart": (24, 24),
    "background": (WIDTH, HEIGHT),
}

# символ сітки -> колір
PALETTE = {
    "k": (50, 25, 75),       # контур
    "p": (150, 100, 210),    # кажанчик
    "P": (195, 160, 240),    # кажанчик світлий
    "d": (105, 65, 160),     # крила
    "w": (255, 255, 255),
    "e": (30, 15, 45),       # очі
    "b": (255, 150, 200),    # рум'янець
    "m": (255, 242, 250),    # маршмелоу
    "M": (232, 198, 232),    # маршмелоу тінь
    "c": (235, 60, 105),     # вишенька
    "g": (110, 185, 100),    # хвостик вишеньки
    "f": (210, 170, 248),    # крем
    "F": (165, 115, 215),    # крем тінь
    "u": (255, 170, 210),    # обгортка кексика
    "U": (232, 118, 180),    # смужки обгортки
    "y": (255, 215, 90),     # золото / посипка
    "O": (225, 150, 45),     # золото темне
    "n": (130, 75, 35),      # контур монетки
    "r": (255, 95, 150),     # серце
}

# сітки спрайтів
BAT_HEAD = [
    "..k..........k..",
    "..kk........kk..",
    "..kPk......kPk..",
    ".kkPpkkkkkkpPkk.",
    ".kppppppppppppk.",
    ".kppppppppppppk.",
    ".kppewppppewppk.",
    ".kppeeppppeeppk.",
    ".kbbeeppppeebbk.",
    ".kppppkppkppppk.",
    ".kpppppkkpppppk.",
    "..kppppwpppppk..",
]
BAT_WINGS_DOWN = [
    "kk.kppPPPPppk.kk",
    "kdk.kpPPPPpk.kdk",
    "kddkkpPPPPpkkddk",
    ".kdddkppppkdddk.",
    "..kkkkppppkkkk..",
    ".....kppppk.....",
]
BAT_WINGS_UP = [
    "kk..kpPPPPpk..kk",
    "kdkkkpPPPPpkkkdk",
    ".kddkpPPPPpkddk.",
    "..kkkppppppkkk..",
    ".....kppppk.....",
    ".....kppppk.....",
]
BAT_LEGS = {
    "idle":  [".....kkkkkk.....", "......k..k......", ".....kk..kk.....", ".....kk..kk....."],
    "run_1": [".....kkkkkk.....", ".....k....k.....", "....kk....kk....", "....kk....kk...."],
    "run_2": [".....kkkkkk.....", "......k..k......", "......kkkk......", "......kkkk......"],
    "jump":  [".....kkkkkk.....", "......k..k......", ".....kk..kk.....", "................"],
}
BAT_FRAMES = {
    "idle": BAT_HEAD + BAT_WINGS_DOWN + BAT_LEGS["idle"],
    "run_1": BAT_HEAD + BAT_WINGS_DOWN + BAT_LEGS["run_1"],
    "run_2": BAT_HEAD + BAT_WINGS_UP + BAT_LEGS["run_2"],
    "jump": BAT_HEAD + BAT_WINGS_UP + BAT_LEGS["jump"],
}

MARSHMALLOW_BODY = [
    "....kkkkkkkkkk....",
    "...kmmmmmmmmmmk...",
    "..kmmmmmmmmmmmmk..",
    ".kmmmmmmmmmmmmmmk.",
    ".kmmkmmmmkmmmmmmk.",
    ".kmmmkmmkmmmmmmmk.",
    ".kmmeemmeemmmmmmk.",
    ".kmmeemmeemmmmmmk.",
    ".kmbbmmmmbbmmmmmk.",
    ".kmmmmkkkmmmmmmmk.",
    ".kmmmkmmmkmmmmmmk.",
    ".kMMMMMMMMMMMMMMk.",
    "..kMMMMMMMMMMMMk..",
    "...kkkkkkkkkkkk...",
]
MARSHMALLOW_FRAMES = (
    MARSHMALLOW_BODY + ["...kk........kk..."],
    MARSHMALLOW_BODY + [".....kk....kk....."],
)

CUPCAKE_TOP = [
    "........gk........",
    ".......kcck.......",
    "......kccwck......",
]
CUPCAKE_BODY = [
    "...kkkkkcckkkkk...",
    "..kfffyffffffyfk..",
    ".kffyfffffffffyfk.",
    "kFFffffffffffffFFk",
    "kFFFFFFFFFFFFFFFFk",
    ".kkkkkkkkkkkkkkkk.",
    "..kuukuuuuuukuuk..",
    "..kuuukuuuukuuuk..",
    "..kuuueuuuueuuuk..",
    "..kubueukkueubuk..",
    "..kUuUuUuUuUuUuk..",
    "...kkkkkkkkkkkk...",
]
CUPCAKE_FRAMES = (
    CUPCAKE_TOP + CUPCAKE_BODY,
    [row[1:] + "." for row in CUPCAKE_TOP] + CUPCAKE_BODY,   # вишенька хитається
)

COIN = [
    "....nnnn....",
    "..nnyyyynn..",
    ".nywyyyyyyn.",
    ".nyyyOOyyyn.",
    "nyyOOOOOOyyn",
    "nyyyOOOOyyyn",
    "nyyyOOOOyyyn",
    "nyyOOyyOOyyn",
    ".nyOyyyyOyn.",
    ".nyyyyyyyyn.",
    "..nnyyyynn..",
    "....nnnn....",
]

HEART = [
    "............",
    ".kkk....kkk.",
    "kwrrrkkrrrrk",
    "kwrrrrrrrrrk",
    "krrrrrrrrrrk",
    "krrrrrrrrrrk",
    ".krrrrrrrrk.",
    "..krrrrrrk..",
    "...krrrrk...",
    "....krrk....",
    ".....kk.....",
    "............",
]


def from_grid(grid, scale=PIXEL):
    # сітка символів -> картинка
    h, w = len(grid), len(grid[0])
    assert all(len(row) == w for row in grid), "рядки сітки різної довжини"
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch in PALETTE:
                surf.set_at((x, y), PALETTE[ch])
    return pygame.transform.scale(surf, (w * scale, h * scale))


def lowres(size, draw):
    # малює в половинному розмірі і збільшує x2
    small = pygame.Surface((size[0] // PIXEL, size[1] // PIXEL), pygame.SRCALPHA)
    draw(small)
    return pygame.transform.scale(small, size)


# малюнки примітивами
def _ground(grass):
    def draw(s):
        w, h = s.get_size()
        s.fill((95, 55, 130))
        for x, y in ((3, 12), (12, 9), (7, 16), (16, 15), (1, 18), (14, 3), (5, 6)):
            s.set_at((x, y), (130, 90, 175))
            s.set_at((x + 1, y), (130, 90, 175))
        if grass:                                    # глазур з патьоками
            pygame.draw.rect(s, (245, 185, 235), (0, 0, w, 5))
            pygame.draw.rect(s, (255, 225, 250), (0, 0, w, 1))
            for x, length in ((3, 2), (4, 1), (11, 3), (12, 2), (13, 1), (17, 1)):
                pygame.draw.line(s, (245, 185, 235), (x, 5), (x, 4 + length))
            for x, y, c in ((2, 2, (120, 220, 255)), (8, 1, (255, 230, 120)),
                            (15, 3, (120, 220, 255)), (18, 1, (255, 255, 255))):
                s.set_at((x, y), c)
    return draw


def _platform(s):
    w, h = s.get_size()
    pygame.draw.rect(s, (90, 50, 120), (0, 0, w, h))
    pygame.draw.rect(s, (215, 150, 235), (1, 1, w - 2, h - 2))
    pygame.draw.rect(s, (255, 235, 250), (1, 1, w - 2, 2))
    pygame.draw.rect(s, (175, 110, 205), (1, h - 3, w - 2, 2))
    for x in (5, 14):
        s.set_at((x, 5), (175, 110, 205))
    for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        s.set_at((x, y), (0, 0, 0, 0))


def _cloud(s):
    outline, body, shade = (120, 90, 175), (238, 230, 255), (205, 190, 240)
    for color, grow in ((outline, 1), (body, 0)):
        for cx, cy, r in ((4, 5, 4), (10, 4, 5), (15, 5, 4)):
            pygame.draw.circle(s, color, (cx, cy), r + grow)
        pygame.draw.rect(s, color, (0, 5 - grow, 20, 4 + grow * 2))
    pygame.draw.line(s, shade, (1, 8), (18, 8))


def _spike(s):
    for left, peak, right in ((0, 3, 6), (7, 10, 13), (14, 16, 19)):
        pts = [(left, 9), (peak, 0), (right, 9)]
        pygame.draw.polygon(s, (200, 150, 255), pts)
        pygame.draw.line(s, (240, 215, 255), (peak, 1), (left + 1, 8))
        pygame.draw.polygon(s, (90, 50, 140), pts, 1)


def _flag(s):
    pygame.draw.rect(s, (90, 50, 140), (2, 3, 3, 37))
    pygame.draw.line(s, (240, 230, 255), (3, 3), (3, 39))
    pygame.draw.polygon(s, (255, 130, 190), [(5, 4), (18, 9), (5, 14)])
    pygame.draw.polygon(s, (150, 50, 110), [(5, 4), (18, 9), (5, 14)], 1)
    for x, y in ((8, 8), (10, 8), (8, 9), (9, 9), (10, 9), (9, 10)):   # сердечко
        s.set_at((x, y), (255, 255, 255))
    for x, y in ((3, 0), (2, 1), (3, 1), (4, 1), (3, 2)):                # зірочка
        s.set_at((x, y), (255, 225, 100))
    pygame.draw.rect(s, (150, 80, 175), (0, 37, 7, 3))


def _background(s):
    w, h = s.get_size()
    top, bottom = (35, 15, 70), (115, 55, 150)
    for y in range(h):
        t = y / h
        pygame.draw.line(s, [int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)],
                         (0, y), (w, y))
    rnd = random.Random(7)
    for _ in range(70):                                  # зірки
        x, y = rnd.randrange(w), rnd.randrange(int(h * 0.65))
        s.set_at((x, y), rnd.choice(((255, 255, 255), (255, 240, 180), (220, 190, 255))))
    for x, y in ((60, 40), (210, 25), (330, 70), (430, 110)):   # великі зірочки
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            s.set_at((x + dx, y + dy), (255, 245, 200))
    # місяць з мордочкою
    mx, my = 390, 48
    pygame.draw.circle(s, (255, 240, 190), (mx, my), 18)
    pygame.draw.circle(s, (240, 215, 160), (mx + 7, my - 6), 3)
    for ex in (mx - 7, mx + 5):
        pygame.draw.line(s, (90, 60, 60), (ex - 2, my + 1), (ex, my - 1))
        pygame.draw.line(s, (90, 60, 60), (ex, my - 1), (ex + 2, my + 1))
    pygame.draw.rect(s, (255, 170, 190), (mx - 12, my + 4, 3, 2))
    pygame.draw.rect(s, (255, 170, 190), (mx + 9, my + 4, 3, 2))
    # пагорби, синус без шва
    for color, base, amp, k in (((70, 35, 110), 215, 22, 2), ((95, 48, 135), 240, 15, 3)):
        pts = [(x, base + amp * math.sin(2 * math.pi * k * x / w)) for x in range(0, w + 1, 4)]
        pygame.draw.polygon(s, color, [(0, h)] + pts + [(w, h)])


FALLBACKS = {
    **{"player_" + name: (lambda g: lambda size: from_grid(g))(grid)
       for name, grid in BAT_FRAMES.items()},
    "marshmallow_1": lambda size: from_grid(MARSHMALLOW_FRAMES[0]),
    "marshmallow_2": lambda size: from_grid(MARSHMALLOW_FRAMES[1]),
    "cupcake_1": lambda size: from_grid(CUPCAKE_FRAMES[0]),
    "cupcake_2": lambda size: from_grid(CUPCAKE_FRAMES[1]),
    "coin": lambda size: from_grid(COIN),
    "heart": lambda size: from_grid(HEART),
    "ground_top": lambda size: lowres(size, _ground(True)),
    "ground": lambda size: lowres(size, _ground(False)),
    "platform": lambda size: lowres(size, _platform),
    "moving_platform": lambda size: lowres(size, _cloud),
    "spike": lambda size: lowres(size, _spike),
    "flag": lambda size: lowres(size, _flag),
    "background": lambda size: lowres(size, _background),
}


def load_image(name):
    # png з images/ або малюнок з коду
    size = SIZES[name]
    path = os.path.join(IMG_DIR, name + ".png")
    if os.path.exists(path):
        image = pygame.image.load(path)
        if pygame.display.get_surface():
            image = image.convert_alpha()
        return pygame.transform.scale(image, size)      # без згладжування
    image = FALLBACKS[name](size)
    return image if image.get_size() == size else pygame.transform.scale(image, size)


def load_images():
    # всі картинки, після set_mode()
    return {name: load_image(name) for name in SIZES}
