import pygame
import sys
import subprocess
import json
pygame.init()

# read saved settings (volume + resolution)
with open("settings.json", "r") as f:
    settings = json.load(f)

info_ecran = pygame.display.Info()
# start with stored resolution, fallback to current display size
try:
    W, H = map(int, settings["fullscreen"].split(","))
except Exception:
    W, H = info_ecran.current_w, info_ecran.current_h

# keep a reference resolution for scaling buttons
ref_W, ref_H = info_ecran.current_w, info_ecran.current_h

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Menu")

#Ecran menu
background = pygame.image.load("Sprite/Menu.png")
background = pygame.transform.scale(background, (W, H))

#MUSIQUE FELICITE MOI LOUIS J'AI TROUVE
pygame.mixer.music.load("Music/Menu.mp3")
pygame.mixer.music.play(-1)  #Boucle infinie

#Couleurs
WHITE = (255,255,255)
TRANSLUCENT_BLUE = (0,80,200,180)
HOWER_BLUE = (0,140,255,220)
SHADOW = (0,0,0)

# fullscreen flag based on current resolution vs display
is_fullscreen = (W, H) == (info_ecran.current_w, info_ecran.current_h)
# make sure the settings dict we read earlier has current values
settings["volume"] = pygame.mixer.music.get_volume()
settings["fullscreen"] = f"{W},{H}"

def set_resolution(newW: int, newH: int, fullscreen: bool = False):
    """Apply a new window size and rescale everything that depends on W/H."""
    global W, H, screen, background, is_fullscreen, settings
    W, H = newW, newH
    is_fullscreen = fullscreen
    screen = pygame.display.set_mode((W, H))
    background = pygame.transform.scale(pygame.image.load("Sprite/Menu.png"), (W, H))
    settings["fullscreen"] = f"{W},{H}"
    for btn in buttons:
        btn.update()


def toggle_fullscreen():
    # switch between a fixed windowed size and fullscreen
    if is_fullscreen:
        set_resolution(1080, 720, fullscreen=False)
    else:
        set_resolution(info_ecran.current_w, info_ecran.current_h, fullscreen=True)

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
        # allow either a ratio (<=1) or a pixel value for vertical placement
        if center_y <= 1:
            self.center_ratio = center_y
        else:
            self.center_ratio = center_y / ref_H

        # these dimensions correspond to the reference resolution
        self.base_width = 640
        self.base_height = 140

        self.update()

    def update(self):
        # recalc size & position based on the current window dimensions
        self.width = self.base_width * W / ref_W
        self.height = self.base_height * H / ref_H
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (W // 2, int(H * self.center_ratio))

    def draw(self,win,mouse_pos):
        # the rect should already be up to date (toggle_fullscreen calls update)
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
    
# build the button list after reference sizes are defined
buttons = [
    Button("Volume up", 0.375, "change_volume_up"),
    Button("Volume down", 0.5, "change_volume_down"),
    Button("Resolution", 0.650, "change_resolution"),
    Button("Retour au menu", 0.825, "quit")
]
# list of window sizes that the resolution button cycles through
liste_resolutions = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (ref_W, ref_H),
]
current_index = 0
for i, res in enumerate(liste_resolutions):
    if (W, H) == res:
        current_index = i
        break

def cycle_resolution():
    global current_index
    current_index = (current_index + 1) % len(liste_resolutions)
    w, h = liste_resolutions[current_index]
    set_resolution(w, h, fullscreen=False)
running = True
clock = pygame.time.Clock()
while running:
    clock.tick(60)
    screen.blit(background,(0,0))

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    title = font_title.render("Option",True,WHITE)
    shadow = font_title.render("Option",True,SHADOW)
    screen.blit(shadow,(W//2 - title.get_width()//2 + 3,103))
    screen.blit(title,(W//2 - title.get_width()//2,100))

    for btn in buttons:
        btn.draw(screen,mouse_pos)
        if btn.is_click(mouse_pos,mouse_pressed):
            pygame.time.delay(200)  #Evite les double click ca crash sinon
            if btn.action == "change_volume_up":
                pygame.mixer.music.set_volume(min(pygame.mixer.music.get_volume() + 0.3, 1.0))
                settings["volume"] = pygame.mixer.music.get_volume()
            elif btn.action == "change_volume_down":
                pygame.mixer.music.set_volume(max(pygame.mixer.music.get_volume() - 0.3, 0.0))
                settings["volume"] = pygame.mixer.music.get_volume()
            elif btn.action == "change_resolution":
                # cycle through predefined window sizes
                cycle_resolution()
            elif btn.action == "quit":
                print("Retour au menu")
                with open("settings.json", "w") as f:
                    json.dump(settings, f)
                pygame.quit()
                subprocess.run(["python","Menu.py"])
                sys.exit()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
pygame.quit()
print("Options fermé")