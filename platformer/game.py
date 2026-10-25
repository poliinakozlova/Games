# головний клас гри
import pygame

from settings import (WIDTH, HEIGHT, FPS, TITLE, START_LIVES, COIN_SCORE, ENEMY_SCORE,
                      STOMP_BOUNCE, LEVEL_COMPLETE_DELAY, HIGHSCORE_FILE, WHITE, PINK,
                      LAVENDER, OVERLAY)
from assets import load_images
from sounds import SoundManager
from levels import LEVELS, Level
from player import Player, JUMP_KEYS
from menu import Menu, draw_pixel_text

CONTROLS_HINT = "Стрілки / A D — рух    Пробіл / W — стрибок    Esc — пауза    R — рестарт"


def load_high_score():
    try:
        with open(HIGHSCORE_FILE) as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def save_high_score(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except OSError:
        pass


class Game:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.images = load_images()
        self.player_frames = {k: self.images["player_" + k]
                              for k in ("idle", "run_1", "run_2", "jump")}
        self.sounds = SoundManager()
        self.fonts = {
            # текст збільшується x2, тому шрифти малі
            "big": pygame.font.Font(None, 44),
            "medium": pygame.font.Font(None, 22),
            "small": pygame.font.Font(None, 15),
        }
        self.menus = {
            "menu": Menu("ПЛАТФОРМЕР", [("Грати", "play"), ("Вихід", "exit")]),
            "paused": Menu("Пауза", [("Продовжити", "resume"), ("Рестарт", "restart"),
                                     ("Меню", "menu")]),
            "game_over": Menu("Гру закінчено", [("Рестарт", "restart"), ("Меню", "menu"),
                                                ("Вихід", "exit")]),
            "victory": Menu("Перемога!", [("Грати знову", "restart"), ("Меню", "menu")]),
        }

        self.high_score = load_high_score()
        self.state = "menu"     # поточний екран
        self.running = True
        self.frame = 0
        self.reset_game()
        self.sounds.play_music()

    # стан гри
    def reset_game(self):
        # скидання рахунку, життів і рівня
        self.score = 0
        self.level_index = 0
        self.load_level(0, START_LIVES)

    def load_level(self, index, lives):
        self.level = Level(LEVELS[index], self.images)
        self.player = Player(self.level.player_start, self.player_frames, self.sounds, lives)
        self.coins_collected = 0
        self.camera_x = 0.0
        self.timer = 0

    def start_playing(self):
        self.reset_game()
        self.state = "playing"
        self.sounds.play_music()

    def finish(self, state, sound):
        # програш або перемога
        self.state = state
        self.high_score = max(self.high_score, self.score)
        save_high_score(self.high_score)
        self.menus[state].subtitle = f"Рахунок: {self.score}    Рекорд: {self.high_score}"
        self.menus[state].selected = 0
        self.sounds.stop_music()
        self.sounds.play(sound)

    def next_level(self):
        self.level_index += 1
        if self.level_index >= len(LEVELS):
            self.finish("victory", "level_complete")
        else:
            self.load_level(self.level_index, self.player.lives)
            self.state = "playing"

    def do_action(self, action):
        self.sounds.play("click")
        if action in ("play", "restart"):
            self.start_playing()
        elif action == "resume":
            self.state = "playing"
        elif action == "menu":
            self.reset_game()
            self.state = "menu"
            self.menus["menu"].selected = 0
            self.sounds.play_music()
        elif action == "exit":
            self.running = False

    # основний цикл
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key in JUMP_KEYS:
                        self.player.jump()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "paused"
                        self.menus["paused"].selected = 0
                    elif event.key == pygame.K_r:
                        self.start_playing()
                elif event.type == pygame.KEYUP and event.key in JUMP_KEYS:
                    self.player.cut_jump()
            elif self.state in self.menus:
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_r
                        and self.state != "menu"):
                    self.do_action("restart")
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                        and self.state == "paused"):
                    self.state = "playing"
                else:
                    action = self.menus[self.state].handle_event(event)
                    if action:
                        self.do_action(action)

    def update(self):
        self.frame += 1
        for coin in self.level.coins:
            coin.update(self.frame)
        if self.state == "playing":
            self.update_playing()
        elif self.state == "level_complete":
            self.timer -= 1
            if self.timer <= 0:
                self.next_level()

    def update_playing(self):
        level, player = self.level, self.player
        player.handle_input(pygame.key.get_pressed())
        for mover in level.movers:
            mover.update()
        player.update(level.solids, level.platforms, level.width)
        for enemy in level.enemies:
            enemy.update(level.solids, level.spikes, level.width)
        level.enemies = [e for e in level.enemies if e.alive or e.dead_timer > 0]
        self.check_collisions()
        self.update_camera()

    def check_collisions(self):
        level, player = self.level, self.player

        # монетки
        for coin in [c for c in level.coins if player.rect.colliderect(c.rect)]:
            level.coins.remove(coin)
            self.score += COIN_SCORE
            self.coins_collected += 1
            self.sounds.play("coin")

        # ворог: зверху - розчавити, збоку - удар
        for enemy in level.enemies:
            if not enemy.alive or not player.rect.colliderect(enemy.rect):
                continue
            if player.prev_bottom <= enemy.rect.top + 8:
                enemy.squash()
                player.vel_y = -STOMP_BOUNCE
                self.score += ENEMY_SCORE
                self.sounds.play("stomp")
            elif not player.invulnerable:
                self.player_hit()
                return

        # шипи
        if not player.invulnerable and any(player.rect.colliderect(s.hitbox)
                                           for s in level.spikes):
            self.player_hit()
            return

        # падіння у прірву
        if player.rect.top > level.height:
            self.player_hit()
            return

        # фініш
        if level.flag and player.rect.colliderect(level.flag.rect):
            self.state = "level_complete"
            self.timer = LEVEL_COMPLETE_DELAY
            self.sounds.play("level_complete")

    def player_hit(self):
        if not self.player.hit():
            self.finish("game_over", "game_over")
        else:
            self.camera_x = 0.0

    def update_camera(self):
        target = self.player.rect.centerx - WIDTH / 2
        target = max(0, min(target, self.level.width - WIDTH))
        self.camera_x += (target - self.camera_x) * 0.15     # плавне слідування

    # малювання
    def draw(self):
        self.draw_background()
        self.draw_world()
        if self.state == "menu":
            self.menus["menu"].draw(self.screen, self.fonts)
            draw_pixel_text(self.screen, self.fonts["small"], CONTROLS_HINT,
                            (WIDTH // 2, HEIGHT - 28), LAVENDER, "center", shadow=2)
            return
        self.draw_hud()
        if self.state in self.menus:
            self.menus[self.state].draw(self.screen, self.fonts)
        elif self.state == "level_complete":
            self.draw_banner(f"Рівень {self.level_index + 1} пройдено!")

    def draw_background(self):
        bg = self.images["background"]
        offset = int(self.camera_x * 0.3) % WIDTH          # паралакс
        self.screen.blit(bg, (-offset, 0))
        self.screen.blit(bg, (WIDTH - offset, 0))

    def blit_sprite(self, sprite):
        cam = int(self.camera_x)
        if sprite.rect.right < cam or sprite.rect.left > cam + WIDTH:
            return
        rect = sprite.image.get_rect(center=sprite.rect.center).move(-cam, 0)
        self.screen.blit(sprite.image, rect)

    def draw_world(self):
        level = self.level
        groups = (level.solids, level.platforms, level.spikes, level.coins,
                  [level.flag] if level.flag else [], level.enemies)
        for group in groups:
            for sprite in group:
                self.blit_sprite(sprite)
        self.player.draw(self.screen, int(self.camera_x))

    def draw_text(self, text, pos, font="small", color=WHITE, anchor="topleft"):
        draw_pixel_text(self.screen, self.fonts[font], text, pos, color, anchor, shadow=2)

    def draw_hud(self):
        for i in range(self.player.lives):
            self.screen.blit(self.images["heart"], (16 + i * 28, 12))
        self.draw_text(f"Рахунок: {self.score}", (16, 44), color=PINK)
        self.screen.blit(self.images["coin"], (14, 74))
        self.draw_text(f"{self.coins_collected}/{self.level.total_coins}", (44, 76))
        self.draw_text(f"Рівень {self.level_index + 1}/{len(LEVELS)}", (WIDTH - 16, 14),
                       anchor="topright", color=PINK)
        self.draw_text(f"Рекорд: {max(self.high_score, self.score)}", (WIDTH - 16, 44),
                       anchor="topright", color=LAVENDER)

    def draw_banner(self, text):
        band = pygame.Surface((WIDTH, 110), pygame.SRCALPHA)
        band.fill(OVERLAY)
        self.screen.blit(band, (0, HEIGHT // 2 - 55))
        self.draw_text(text, (WIDTH // 2, HEIGHT // 2), font="big", color=PINK,
                       anchor="center")
