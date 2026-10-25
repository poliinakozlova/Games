# гравець
import pygame

from settings import (GRAVITY, MAX_FALL, PLAYER_SPEED, JUMP_POWER, JUMP_CUT,
                      INVULNERABLE_FRAMES)
from sprites import MovingPlatform

LEFT_KEYS = (pygame.K_LEFT, pygame.K_a)
RIGHT_KEYS = (pygame.K_RIGHT, pygame.K_d)
JUMP_KEYS = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)


class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, frames, sounds, lives):
        super().__init__()
        self.frames = frames            # idle, run_1, run_2, jump
        self.sounds = sounds
        self.lives = lives
        self.start_pos = start_pos      # (x, y) низу персонажа
        self.image = frames["idle"]
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        # на старт рівня
        self.rect.midbottom = self.start_pos
        self.pos_x, self.pos_y = float(self.rect.x), float(self.rect.y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.riding = None              # платформа під гравцем
        self.prev_bottom = self.rect.bottom
        self.facing_right = True
        self.anim = 0
        self.invulnerable = 0

    # керування
    def handle_input(self, keys):
        # рух вліво-вправо
        self.vel_x = 0
        if any(keys[k] for k in LEFT_KEYS):
            self.vel_x -= PLAYER_SPEED
        if any(keys[k] for k in RIGHT_KEYS):
            self.vel_x += PLAYER_SPEED
        if self.vel_x:
            self.facing_right = self.vel_x > 0

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_POWER
            self.on_ground = False
            self.riding = None
            self.sounds.play("jump")

    def cut_jump(self):
        # відпустив клавішу - стрибок нижчий
        if self.vel_y < -JUMP_CUT:
            self.vel_y = -JUMP_CUT

    # фізика
    def update(self, solids, platforms, level_width):
        # їдемо разом з платформою
        if self.riding:
            self.pos_x += self.riding.dx
            self.pos_y += self.riding.dy
            self.rect.y = round(self.pos_y)

        # рух по x і зіткнення збоку
        self.pos_x += self.vel_x
        self.rect.x = round(self.pos_x)
        for block in solids:
            if self.rect.colliderect(block.rect):
                if self.rect.centerx < block.rect.centerx:
                    self.rect.right = block.rect.left
                else:
                    self.rect.left = block.rect.right
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, level_width)
        self.pos_x = self.rect.x

        # гравітація і зіткнення по y
        self.prev_bottom = self.rect.bottom
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL)
        self.pos_y += self.vel_y
        self.rect.y = round(self.pos_y)
        self.on_ground = False
        self.riding = None
        for block in solids:
            if self.rect.colliderect(block.rect):
                if self.vel_y > 0:                       # приземлились
                    self.rect.bottom = block.rect.top
                    self.on_ground = True
                elif self.vel_y < 0:                     # вдарились головою
                    self.rect.top = block.rect.bottom
                self.vel_y = 0
        # на платформу стаємо тільки зверху
        if self.vel_y >= 0:
            for plat in platforms:
                if (self.rect.colliderect(plat.rect)
                        and self.prev_bottom <= plat.rect.top - plat.dy + 1):
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    if isinstance(plat, MovingPlatform):
                        self.riding = plat
        self.pos_y = self.rect.y

        if self.invulnerable:
            self.invulnerable -= 1
        self._animate()

    def hit(self):
        # мінус життя, true якщо ще є
        self.lives -= 1
        self.sounds.play("hurt")
        if self.lives > 0:
            self.reset_position()
            self.invulnerable = INVULNERABLE_FRAMES
        return self.lives > 0

    # малювання
    def _animate(self):
        if not self.on_ground:
            name = "jump"
        elif self.vel_x:
            self.anim += 1
            name = "run_1" if (self.anim // 8) % 2 == 0 else "run_2"
        else:
            name = "idle"
        image = self.frames[name]
        self.image = image if self.facing_right else pygame.transform.flip(image, True, False)

    def draw(self, surface, camera_x):
        if self.invulnerable and (self.invulnerable // 5) % 2:   # блимання
            return
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))
