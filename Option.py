import pygame
import sys
import subprocess
pygame.init()


#Promis je documente cette fois 
info_ecran = pygame.display.Info()
W,H = info_ecran.current_w, info_ecran.current_h
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Menu")

#Ecran menu
background = pygame.image.load("Menu.png")
background = pygame.transform.scale(background,(W,H))

#MUSIQUE FELICITE MOI LOUIS J'AI TROUVE
pygame.mixer.music.load("Menu.mp3")
pygame.mixer.music.play(-1)  #Boucle infinie

#Couleurs
WHITE = (255,255,255)
TRANSLUCENT_BLUE = (0,80,200,180)
HOWER_BLUE = (0,140,255,220)
SHADOW = (0,0,0)


#Police
try:
    font_title = pygame.font.Font("Pixel.ttf", 144)
    font_button = pygame.font.Font("Pixel.ttf", 72)
except:
    font_title = pygame.font.SysFont(None, 144)
    font_button = pygame.font.SysFont(None, 72)

class Button:
    def __init__(self,text,center_y,action):
        self.text = text
        self.action = action
        self.center_y = center_y
        self.width,self.height = 640,140
        self.rect = pygame.Rect(0,0,self.width,self.height)
        self.rect.center = (W//2,self.center_y)

    def draw(self,win,mouse_pos):
        is_over = self.rect.collidepoint(mouse_pos)
        color = HOWER_BLUE if is_over else TRANSLUCENT_BLUE   #change la couleur si on passe le boutton dessus
        button_surface = pygame.Surface((self.width,self.height),pygame.SRCALPHA)
        pygame.draw.rect(button_surface,color,(0,0,self.width,self.height),border_radius=16)
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
    Button("Music",720,"change_music"),
    Button("Theme",900,"change_theme"),
    Button("Retour au menu",1080,"quit")
]
def resolution():
    global current_index,liste_resolutions
    if current_index >= len(liste_resolutions) - 1:
        current_index = 0
    else:
        current_index = (current_index + 1) 
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
            if btn.action == "change_music":
                print("Music, j'ai pas encore fait")
            elif btn.action == "change_theme":
                print("Options, j'ai pas encore fait")
            elif btn.action == "quit":
                print("Retour au menu")
                pygame.quit()
                subprocess.run(["python","Menu.py"])
                sys.exit()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
pygame.quit()
print("Options fermé")