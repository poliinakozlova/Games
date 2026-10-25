# карти рівнів, 1 символ = 1 клітинка
# земля #, платформа -, старт P, монетка C, фініш F
# маршмелоу E, кексик U, шипи ^
# рухома вправо: HH~~~, шлях = к-сть ~
# рухома вгору: V, шлях = к-сть | над нею
from settings import TILE, ENEMY_SPEED, CUPCAKE_SPEED
from sprites import Block, Platform, MovingPlatform, Coin, Spike, Flag, Enemy

LEVEL_1 = [
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "               CC                                               ",
    "              ----                                              ",
    "                                                                ",
    "         C C             C C                       C C          ",
    "        -----           -----                     -----         ",
    "                   C                                            ",
    "  P                        ^^    E             C C C    U    F  ",
    "##################   ##################HH~~~~###################",
    "##################   ##################      ###################",
]

LEVEL_2 = [
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                                   CCCC               C  C      ",
    "                                                  ######              ----      ",
    "                         C C           CC     |   ######                        ",
    "     CC                 -----         ----    |   ######  C      CC             ",
    "    ----                                      |   ######        ----            ",
    "               C                              |   ######  --                    ",
    "  P                  ^^   E    HH~~~~~        VV  ######          U  ^^   E  F  ",
    "##############   ##############       ##################     ###################",
    "##############   ##############       ##################     ###################",
]

LEVEL_3 = [
    "                                                                                                ",
    "                                                                                                ",
    "                                                                                                ",
    "                                                                                                ",
    "                                                              CCCC                              ",
    "                                                             ------                             ",
    "                                                          |                                     ",
    "                                                          |           C                         ",
    "                            CC                            |          ---                        ",
    "                C C        ----                C  C       |                      C C            ",
    "               -----                                      |                     -----           ",
    "           C                        #           --        |                                     ",
    "  P            ^  E    HH~~~~~~~~~  # ^^  U          E    VV  U             ^^  U   ^^  E    F  ",
    "##########   ##########           ############      ############        ########################",
    "##########   ##########           ############      ############        ########################",
]

LEVELS = (LEVEL_1, LEVEL_2, LEVEL_3)     # кортеж рівнів


class Level:
    # будує об'єкти з карти

    def __init__(self, layout, images):
        width = max(len(row) for row in layout)
        rows = [row.ljust(width) for row in layout]

        self.solids = []          # блоки землі
        self.platforms = []       # всі платформи
        self.movers = []          # тільки рухомі
        self.coins = []
        self.spikes = []
        self.enemies = []
        self.flag = None
        self.player_start = (TILE, TILE * (len(rows) - 2))
        # тип ворога -> (кадри, швидкість)
        enemy_types = {
            "E": ((images["marshmallow_1"], images["marshmallow_2"]), ENEMY_SPEED),
            "U": ((images["cupcake_1"], images["cupcake_2"]), CUPCAKE_SPEED),
        }

        for r, row in enumerate(rows):
            c = 0
            while c < width:
                ch = row[c]
                x, y = c * TILE, r * TILE
                if ch == "#":
                    top = r == 0 or rows[r - 1][c] != "#"
                    self.solids.append(Block(x, y, images["ground_top" if top else "ground"]))
                elif ch == "-":
                    self.platforms.append(Platform(x, y, images["platform"]))
                elif ch in "HV":
                    n = self._run_length(row, c, ch)
                    if ch == "H":
                        distance = self._run_length(row, c + n, "~")
                    else:
                        distance = sum(1 for _ in self._column_up(rows, r, c, "|"))
                    mover = MovingPlatform(x, y, n, images["moving_platform"],
                                           ch.lower(), distance)
                    self.movers.append(mover)
                    self.platforms.append(mover)
                    c += n
                    continue
                elif ch == "C":
                    self.coins.append(Coin(x, y, images["coin"]))
                elif ch == "^":
                    self.spikes.append(Spike(x, y, images["spike"]))
                elif ch in enemy_types:
                    frames, speed = enemy_types[ch]
                    self.enemies.append(Enemy(x, y, frames, speed))
                elif ch == "F":
                    self.flag = Flag(x, y, images["flag"])
                elif ch == "P":
                    self.player_start = (x + TILE // 2, y + TILE)
                c += 1

        self.width = width * TILE
        self.height = len(rows) * TILE
        self.total_coins = len(self.coins)

    @staticmethod
    def _run_length(row, start, ch):
        n = 0
        while start + n < len(row) and row[start + n] == ch:
            n += 1
        return n

    @staticmethod
    def _column_up(rows, r, c, ch):
        r -= 1
        while r >= 0 and rows[r][c] == ch:
            yield r
            r -= 1
