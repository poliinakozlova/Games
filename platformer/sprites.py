# ігрові об'єкти
import math

import pygame

from settings import TILE, GRAVITY, MAX_FALL, PLATFORM_SPEED


class Block(pygame.sprite.Sprite):
    # блок землі

    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))


class Platform(pygame.sprite.Sprite):
    # платформа, крізь яку можна стрибнути знизу
    dx = dy = 0            # зміщення за кадр

    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))


class MovingPlatform(Platform):
    # рухома платформа: h - вправо, v - вгору

    def __init__(self, x, y, tiles_wide, tile_image, axis, distance):
        image = pygame.Surface((tiles_wide * TILE, tile_image.get_height()), pygame.SRCALPHA)
        for i in range(tiles_wide):
            image.blit(tile_image, (i * TILE, 0))
        super().__init__(x, y, image)
        self.axis = axis
        self.start = (x, y)
        self.distance = distance * TILE
        self.direction = 1 if axis == "h" else -1

    def update(self):
        step = PLATFORM_SPEED * self.direction
        if self.axis == "h":
            self.rect.x += step
            self.dx, self.dy = step, 0
            offset = self.rect.x - self.start[0]
        else:
            self.rect.y += step
            self.dx, self.dy = 0, step
            offset = self.start[1] - self.rect.y
        if offset >= self.distance or offset <= 0:
            self.direction *= -1


class Coin(pygame.sprite.Sprite):
    # монетка, що крутиться

    def __init__(self, x, y, image):
        super().__init__()
        self.base_image = image
        self.image = image
        self.rect = image.get_rect(center=(x + TILE // 2, y + TILE // 2))
        self.phase = (x + y) * 0.01

    def update(self, frame):
        scale = abs(math.cos(frame * 0.06 + self.phase))
        w = max(2, int(self.base_image.get_width() * scale))
        self.image = pygame.transform.scale(self.base_image, (w, self.base_image.get_height()))


class Spike(pygame.sprite.Sprite):
    # шипи, hitbox менший за картинку

    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(bottomleft=(x, y + TILE))
        self.hitbox = self.rect.inflate(-12, -8).move(0, 4)


class Flag(pygame.sprite.Sprite):
    # фініш рівня

    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(bottomleft=(x, y + TILE))


class Enemy(pygame.sprite.Sprite):
    # ворог розвертається біля стін і обривів

    def __init__(self, x, y, frames, speed):
        super().__init__()
        self.frames = frames                      # 2 кадри анімації
        self.image = frames[0]
        self.rect = self.image.get_rect(midbottom=(x + TILE // 2, y + TILE))
        self.pos_x, self.pos_y = float(self.rect.x), float(self.rect.y)
        self.vel_x = -speed
        self.vel_y = 0.0
        self.anim = 0
        self.alive = True
        self.dead_timer = 0

    def squash(self):
        # розчавили стрибком
        self.alive = False
        self.dead_timer = 30
        w, h = self.rect.size
        self.image = pygame.transform.scale(self.frames[0], (w, h // 3))
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def update(self, solids, spikes, level_width):
        if not self.alive:
            self.dead_timer -= 1
            return

        # гравітація
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL)
        self.pos_y += self.vel_y
        self.rect.y = round(self.pos_y)
        on_ground = False
        for block in solids:
            if self.rect.colliderect(block.rect) and self.vel_y > 0:
                self.rect.bottom = block.rect.top
                self.vel_y = 0
                on_ground = True
        self.pos_y = self.rect.y

        # горизонтальний рух
        self.pos_x += self.vel_x
        self.rect.x = round(self.pos_x)
        turn = False
        for obstacle in [b.rect for b in solids] + [s.rect for s in spikes]:
            if self.rect.colliderect(obstacle):
                if self.vel_x > 0:
                    self.rect.right = obstacle.left
                else:
                    self.rect.left = obstacle.right
                turn = True
        # обрив попереду?
        if on_ground:
            front_x = self.rect.right + 1 if self.vel_x > 0 else self.rect.left - 1
            if not any(b.rect.collidepoint(front_x, self.rect.bottom + 2) for b in solids):
                turn = True
        if self.rect.left <= 0 or self.rect.right >= level_width:
            turn = True
        if turn:
            self.vel_x = -self.vel_x
        self.pos_x = self.rect.x

        # кадри дивляться вліво
        self.anim += 1
        frame = self.frames[(self.anim // 12) % 2]
        self.image = pygame.transform.flip(frame, True, False) if self.vel_x > 0 else frame
