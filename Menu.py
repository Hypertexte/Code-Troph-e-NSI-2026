import pygame
import sys
import subprocess
import json

pygame.init()

with open("settings.json", "r") as f:
    settings = json.load(f)
volume = settings.get("volume", 1.0)


#auto scale
W, H = 1280, 720
LOG_W, LOG_H = 1920, 1080
screen = pygame.display.set_mode((W, H))
logical_screen = pygame.Surface((LOG_W, LOG_H))
pygame.display.set_caption("Menu")


background = pygame.image.load("Sprite/Menu.png")
background = pygame.transform.scale(background, (LOG_W, LOG_H))

#musique
pygame.mixer.music.load("Music/Menu.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(volume)

#couleurs
WHITE = (255, 255, 255)
TRANSLUCENT_BLUE = (0, 80, 200, 180)
HOWER_BLUE = (0, 140, 255, 220)
SHADOW = (0, 0, 0)

#image/texte
try:
    font_title = pygame.font.Font("Police/Pixel.ttf", 144)
    font_button = pygame.font.Font("Police/Pixel.ttf", 72)
except:
    font_title = pygame.font.SysFont(None, 144)
    font_button = pygame.font.SysFont(None, 72)


class Button:
    def __init__(self, text, center_y, action):
        self.text = text
        self.action = action
        self.width = 640
        self.height = 140
        self.rect = pygame.Rect(0, 0, self.width, self.height)

        if center_y <= 1:
            self.rect.center = (LOG_W // 2, int(LOG_H * center_y))
        else:
            self.rect.center = (LOG_W // 2, int(center_y))

    def draw(self, win, mouse_pos):
        is_over = self.rect.collidepoint(mouse_pos)
        color = HOWER_BLUE if is_over else TRANSLUCENT_BLUE
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, color, (0, 0, self.rect.width, self.rect.height), border_radius=16)
        win.blit(button_surface, self.rect)

        text_surf = font_button.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        shadow = font_button.render(self.text, True, SHADOW)
        win.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
        win.blit(text_surf, text_rect)

    def is_click(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]


buttons = [Button("Jouer", 0.35, "new"),Button("Options", 0.6, "options"),Button("Quitter", 0.85, "quit")]

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    logical_screen.blit(background, (0, 0))

    real_mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    logical_mouse_pos = (int(real_mouse_pos[0] * (LOG_W / W)),int(real_mouse_pos[1] * (LOG_H / H)))

    title = font_title.render("Jeu ?", True, WHITE)
    shadow = font_title.render("Jeu ?", True, SHADOW)
    logical_screen.blit(shadow, (LOG_W // 2 - title.get_width() // 2 + 3, LOG_H // 10 - 3))
    logical_screen.blit(title, (LOG_W // 2 - title.get_width() // 2, LOG_H // 10))

    for btn in buttons:
        btn.draw(logical_screen, logical_mouse_pos)
        if btn.is_click(logical_mouse_pos, mouse_pressed):
            pygame.time.delay(200)
            if btn.action == "new":
                pygame.quit()
                subprocess.run(["python", "Game.py"])
                sys.exit()
            elif btn.action == "options":
                pygame.quit()
                subprocess.run(["python", "Option.py"])
                sys.exit()
            elif btn.action == "quit":
                running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    scaled_surface = pygame.transform.scale(logical_screen, (W, H))
    screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()

pygame.quit()