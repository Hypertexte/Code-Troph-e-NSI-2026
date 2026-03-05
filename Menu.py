import pygame
import sys
import subprocess
import json
pygame.init()


#Promis je documente cette fois                         #J'ai oublié a la fin de documenter, mais c'est pas grave, c'est pas comme si c'était important de comprendre le code du truc que tu code :/


with open("settings.json", "r") as f:
    settings = json.load(f)
volume = settings.get("volume", 1.0)
W, H = map(int, settings.get("fullscreen", f"{pygame.display.Info().current_w},{pygame.display.Info().current_h}").split(","))

# keep a reference resolution for scaling
ref_W, ref_H = W, H

# allow the window to be resizable so we can react to manual changes if needed
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Menu")

#Ecran menu
background = pygame.image.load("Sprite/Menu.png")
background = pygame.transform.scale(background,(W,H))

#MUSIQUE FELICITE MOI LOUIS J'AI TROUVE
pygame.mixer.music.load("Music/Menu.mp3")
pygame.mixer.music.play(-1)  #Boucle infinie
pygame.mixer.music.set_volume(volume)

#Couleurs
WHITE = (255,255,255)
TRANSLUCENT_BLUE = (0,80,200,180)
HOWER_BLUE = (0,140,255,220)
SHADOW = (0,0,0)
NOIR = (0,0,0)

#Police
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
        # store a base vertical position in pixels relative to reference height
        if center_y <= 1:
            # center_y given as a ratio; convert to pixel for base
            self.base_center_y = center_y * ref_H
        else:
            # direct pixel position
            self.base_center_y = center_y

        self.base_width = 640
        self.base_height = 140
        self.update()

    def update(self):
        # recompute dimensions/position when window size changes
        self.width = self.base_width * W / ref_W
        self.height = self.base_height * H / ref_H
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        # scale vertical position from the stored base value
        self.rect.center = (W // 2, int(self.base_center_y * H / ref_H))

    def draw(self, win, mouse_pos):
        is_over = self.rect.collidepoint(mouse_pos)
        color = HOWER_BLUE if is_over else TRANSLUCENT_BLUE   #change la couleur si on passe le boutton dessus
        button_surface = pygame.Surface((self.rect.width,self.rect.height),pygame.SRCALPHA)
        pygame.draw.rect(button_surface,color,(0,0,self.rect.width,self.rect.height),border_radius=16)
        win.blit(button_surface,self.rect)
        text_surf = font_button.render(self.text,True,WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        shadow = font_button.render(self.text,True,SHADOW)
        win.blit(shadow,(text_rect.x+2,text_rect.y+2))
        win.blit(text_surf,text_rect)
    
    def is_click(self,mouse_pos,mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]
    
#Liste bouton
buttons = [
    Button("Jouer", 0.35, "new"),
    Button("Options", 0.6, "options"),
    Button("Quitter", 0.85, "quit")
]

running = True
clock = pygame.time.Clock()
while running:
    clock.tick(60)
    screen.blit(background,(0,0))

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    title = font_title.render("Jeu ?",True,WHITE)
    shadow = font_title.render("Jeu ?",True,SHADOW)
    screen.blit(shadow,(W//2 - title.get_width()//2 + 3,H//10 - 3))
    screen.blit(title,(W//2 - title.get_width()//2,H//10))

    for btn in buttons:
        btn.draw(screen,mouse_pos)
        if btn.is_click(mouse_pos,mouse_pressed):
            pygame.time.delay(200)  #Evite les double click ca crash sinon
            if btn.action == "new":
                print("Lancement du jeu")
                pygame.quit()
                subprocess.run(["python","Game.py"])
                sys.exit()
            elif btn.action == "options":
                print("Ouverture des options")
                pygame.quit()
                subprocess.run(["python","Option.py"])
                sys.exit()
            elif btn.action == "quit":
                running = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # support manual resizing
            W, H = event.w, event.h
            screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
            background = pygame.transform.scale(pygame.image.load("Sprite/Menu.png"),(W,H))
            for btn in buttons:
                btn.update()

    pygame.display.flip()
pygame.quit()
print("Menu fermé")