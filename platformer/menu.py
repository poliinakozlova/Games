# кнопки, меню та піксельний текст
import pygame

from settings import (WIDTH, HEIGHT, WHITE, SHADOW, PINK, LAVENDER, OVERLAY,
                      BUTTON_COLOR, BUTTON_HOVER, BUTTON_BORDER)


def pixel_text(font, text, color):
    # піксельний текст x2
    label = font.render(text, False, color)
    return pygame.transform.scale(label, (label.get_width() * 2, label.get_height() * 2))


def draw_pixel_text(surface, font, text, pos, color=WHITE, anchor="topleft", shadow=3):
    label = pixel_text(font, text, color)
    rect = label.get_rect(**{anchor: pos})
    if shadow:
        surface.blit(pixel_text(font, text, SHADOW), rect.move(shadow, shadow))
    surface.blit(label, rect)
    return rect


def draw_pixel_box(surface, rect, fill, border=BUTTON_BORDER, step=4):
    # прямокутник з піксельними кутами
    x, y, w, h = rect
    pygame.draw.rect(surface, border, (x + step, y, w - 2 * step, h))
    pygame.draw.rect(surface, border, (x, y + step, w, h - 2 * step))
    inner = pygame.Rect(rect).inflate(-2 * step, -2 * step)
    pygame.draw.rect(surface, fill, (inner.x + step, inner.y, inner.w - 2 * step, inner.h))
    pygame.draw.rect(surface, fill, (inner.x, inner.y + step, inner.w, inner.h - 2 * step))
    # відблиск зверху
    light = [min(255, c + 45) for c in fill]
    pygame.draw.rect(surface, light, (inner.x + step, inner.y, inner.w - 2 * step, step))


class Button:
    def __init__(self, text, action, center, size=(280, 60)):
        self.text = text
        self.action = action
        self.rect = pygame.Rect((0, 0), size)
        self.rect.center = center

    def draw(self, surface, font, selected):
        rect = self.rect.move(0, -3) if selected else self.rect
        draw_pixel_box(surface, self.rect.move(0, 6), SHADOW)                 # тінь
        draw_pixel_box(surface, rect, BUTTON_HOVER if selected else BUTTON_COLOR)
        draw_pixel_text(surface, font, self.text, rect.center, WHITE, "center", shadow=2)
        if selected:                                                          # сердечко-курсор
            draw_pixel_text(surface, font, "<3", (rect.left - 14, rect.centery), PINK,
                            "midright", shadow=2)


class Menu:
    # items - список кортежів (текст, дія)

    def __init__(self, title, items, subtitle=""):
        self.title = title
        self.subtitle = subtitle
        start_y = HEIGHT // 2 + 20
        self.buttons = [Button(text, action, (WIDTH // 2, start_y + i * 80))
                        for i, (text, action) in enumerate(items)]
        self.selected = 0

    def handle_event(self, event):
        # повертає дію кнопки або None
        if event.type == pygame.MOUSEMOTION:
            for i, button in enumerate(self.buttons):
                if button.rect.collidepoint(event.pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    return button.action
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.buttons)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self.buttons[self.selected].action
        return None

    def draw(self, surface, fonts):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        surface.blit(overlay, (0, 0))

        title_y = HEIGHT // 2 - 150
        draw_pixel_text(surface, fonts["big"], self.title, (WIDTH // 2, title_y), PINK,
                        "center", shadow=5)
        if self.subtitle:
            draw_pixel_text(surface, fonts["medium"], self.subtitle,
                            (WIDTH // 2, title_y + 70), LAVENDER, "center")
        for i, button in enumerate(self.buttons):
            button.draw(surface, fonts["medium"], i == self.selected)
