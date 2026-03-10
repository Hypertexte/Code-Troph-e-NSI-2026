import math
import pygame
from random import randint
import sys
import json

pygame.init()
pygame.mixer.init()

with open("settings.json", "r") as f:
    settings = json.load(f)
volume = settings.get("volume", 1.0)

#auto scale
info_ecran = pygame.display.Info()
W, H = info_ecran.current_w, info_ecran.current_h
LOG_W, LOG_H = 1920, 1080
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
logical_screen = pygame.Surface((LOG_W, LOG_H))
pygame.display.set_caption("Jeu")
clock = pygame.time.Clock()

#musique
pygame.mixer.music.load("Music/Menu.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(volume)
FPS = 60

#sprite /  texte
try:
    font_title = pygame.font.Font("Police/Pixel.ttf", 144)
    font_button = pygame.font.Font("Police/Pixel.ttf", 72)
except:
    font_title = pygame.font.SysFont(None, 144)
    font_button = pygame.font.SysFont(None, 72)

fireball_sprite = pygame.image.load("Sprite/Boule de feu.png")
fireball_sprite = pygame.transform.scale(fireball_sprite, (40, 40))
fireball_sprite = pygame.transform.rotate(fireball_sprite, 180)
fireball_sprite.convert_alpha()
is_fireball_rotated = False

img_player_idle = pygame.image.load("Sprite/player_idle.png")
img_player_idle = pygame.transform.scale(img_player_idle, (80, 160))
img_player_idle.convert_alpha()

img_player_left = pygame.image.load("Sprite/player_left.png")
img_player_left = pygame.transform.scale(img_player_left, (80, 160))
img_player_left.convert_alpha()

img_player_right = pygame.image.load("Sprite/player_right.png")
img_player_right = pygame.transform.scale(img_player_right, (80, 160))
img_player_right.convert_alpha()

img_player_jump = pygame.image.load("Sprite/player_jumping.png")
img_player_jump = pygame.transform.scale(img_player_jump, (80, 160))
img_player_jump.convert_alpha()

img_sprite_boss = pygame.image.load("Sprite/Sprite boss.png")
img_sprite_boss = pygame.transform.scale(img_sprite_boss, (240, 240))
img_sprite_boss.convert_alpha()

arrow_sprite = pygame.image.load("Sprite/Player arrow new.png")
arrow_sprite = pygame.transform.scale(arrow_sprite, (160, 160))
arrow_sprite.convert_alpha()

background = pygame.image.load("Sprite/background.jpg")
background = pygame.transform.scale(background, (LOG_W, LOG_H))

img_consumable = pygame.image.load("Sprite/consomable.png")
img_consumable = pygame.transform.scale(img_consumable, (40, 40))

#couleur
noir = (0, 0, 0)
bleue = (50, 50, 150)
blanc = (255, 255, 255)
rouge = (255, 0, 0)
vert = (0, 255, 0)
marron = (33, 33, 33)
phase_boss = 1


#class
class entity:
    def __init__(self, pos_x, pos_y, x, y, g, j, double_j, health):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.x = x
        self.y = y
        self.g = g
        self.j = j
        self.double_j = double_j
        self.health = health


class cooldown:
    def __init__(self, dash, plat, jump, a_attack, b_attack):
        self.dash = dash
        self.plat = plat
        self.jump = jump
        self.a_attack = a_attack
        self.b_attack = b_attack


player = entity(100, 100, 40, 80, 0, 0, 0, 100)
plat = entity(0, 0, 120, 40, 0, 0, 0, -1)
boss = entity(LOG_W - 50, LOG_H - 50, 120, 120, 0, 0, 0, 1000)

player_cool = cooldown(0, 0, 0, 0, 0)
boss_cool = cooldown(0, 0, 0, 0, 0)
consumable_cool = cooldown(0, 0, 0, 0, 0)

#variables
list_fireball = []
list_arrow = []
list_spike = []
list_consumable = []
list_consumable_fixe = []
double_arrow = False
double_arrow_timer = 0
player_moving_left = False
player_moving_right = False
player_jumping = False

#================================================================================================================================================================================
#FONCTIONS

#infos/debug
def get_mouse_pos():
    x, y = pygame.mouse.get_pos()
    return int(x * (LOG_W / W)), int(y * (LOG_H / H))

def hitbox(s, a):
    if s.pos_x + s.x > a.pos_x and a.pos_x + a.x > s.pos_x and s.pos_y + s.y > a.pos_y and a.pos_y + a.y > s.pos_y:
        return True
    return False

def sprite_player_choice():
    if player_moving_left:
        sprite_player = img_player_right
    elif player_moving_right:
        sprite_player = img_player_left
    elif player_jumping:
        sprite_player = img_player_jump
    else:
        sprite_player = img_player_idle
    return sprite_player

def get_trajectory_points(start_x, start_y, vel_x, vel_y):
    points = []
    x, y = start_x, start_y
    vx, vy = vel_x, vel_y
    floor_limit = LOG_H - 40
    for _ in range(10):
        points.append((int(x), int(y)))
        x += vx
        y += vy
        vy += 0.40
        if y >= floor_limit or x < 0 or x > LOG_W:
            break
    return points

def debug(a):
    if a.pos_y + a.y > LOG_H - 40:
        a.pos_y = LOG_H - 40 - a.y
        a.g = 0
        if a == player:
            player_cool.jump = 0

    if a.pos_x < 40:
        a.pos_x = 40

    if a.pos_x + a.x > LOG_W - 40:
        a.pos_x = LOG_W - 40 - a.x



#player
def player_arrow(keys):
    x, y = get_mouse_pos()
    buttons = pygame.mouse.get_pressed()
    gravity = 0.40
    floor_limit = LOG_H - 40

    if buttons[0] and player_cool.a_attack == 0:
        dx = x - player.pos_x + 10
        dy = y - player.pos_y + 8
        distance = math.hypot(dx, dy)
        if distance != 0:
            speed = 30
            vel_x = (dx / distance) * speed
            vel_y = (dy / distance) * speed
        else:
            vel_x = 0
            vel_y = 0
        new_arrow = entity(player.pos_x + 10, player.pos_y + 8, 20, 20, vel_y, vel_x, 0, 1)
        list_arrow.append(new_arrow)
        if double_arrow:
            new_arrow2 = entity(player.pos_x + 10, player.pos_y + 48, 20, 20, vel_y, vel_x, 0, 1)
            list_arrow.append(new_arrow2)
        player_cool.a_attack = 120

    if player_cool.a_attack > 0:
        player_cool.a_attack -= 1

    for arrow in list_arrow:
        if arrow.pos_y + arrow.y < floor_limit and not hitbox(arrow, plat):
            arrow.g += gravity
            arrow.pos_x += arrow.j
            arrow.pos_y += arrow.g
        else:
            list_arrow.remove(arrow)
        if hitbox(arrow, boss):
            list_arrow.remove(arrow)
            boss.health = boss.health - 100

def temp_plat(keys):
    if keys[pygame.K_s] and player_cool.plat == 0:
        plat.pos_x = player.pos_x - 40
        plat.pos_y = player.pos_y + 84
        player_cool.plat = 300

    if player_cool.plat > 0:
        player_cool.plat = player_cool.plat - 1
        if player_cool.plat <= 180:
            plat.pos_y = 2100

    if hitbox(player, plat) == True:
        if player.pos_y > plat.pos_y:
            player.pos_y = plat.pos_y + 40
            player.j = 30
        if player.pos_y < plat.pos_y:
            player.g = 0
            player.pos_y = plat.pos_y - 80
            player.j = 14
            player_cool.jump = 0


def gravity():
    floor_limit = LOG_H - 10
    if player.pos_y + player.y < floor_limit and hitbox(player, plat) == False:
        player.g = 30 - player.j
        player.pos_y = player.pos_y + player.g
        player.j = player.j / 1.05
    elif hitbox(player, plat) == False:
        player.g = 0
        player.pos_y = floor_limit - player.y
        player_cool.jump = 0

def jump(keys):
    global player_jumping
    if player.g == 0 and keys[pygame.K_z] and player_cool.jump == 0:
        player.j = 60
        player.pos_y = player.pos_y - 40
        player.double_j = 1
        player_cool.jump = 1
        player_jumping = True
    elif keys[pygame.K_z] and player.g > 0 and player.double_j > 0:
        player.j = 60
        player.double_j = player.double_j - 1
        player_jumping = True
    else:
        player_jumping = False


def moove(keys):
    direct = 0
    global player_moving_left, player_moving_right
    if keys[pygame.K_d]:
        player.pos_x += 10
        direct = 1
        player_moving_left = True
    if keys[pygame.K_q]:
        player.pos_x -= 10
        direct = -1
        player_moving_right = True
    if not keys[pygame.K_d]:
        player_moving_left = False
    if not keys[pygame.K_q]:
        player_moving_right = False

    if keys[pygame.K_LSHIFT] and player_cool.dash == 0:
        player.pos_x = player.pos_x + 100 * direct
        player_cool.dash = 60

    if player_cool.dash > 0:
        player_cool.dash = player_cool.dash - 1



#boss
def boss_gravity():
    floor_limit = LOG_H - 10
    if boss.pos_y + boss.y < floor_limit:
        boss.g = 7.5 - boss.j
        boss.pos_y = boss.pos_y + boss.g
        boss.j = boss.j / 1.05
    else:
        boss.g = 0
        boss.pos_y = floor_limit - boss.y


def boss_fireball():
    if boss_cool.a_attack == 0:
        new_fb = entity(boss.pos_x - 5, boss.pos_y + randint(20, 80), 20, 20, 0, 0, 0, 1)
        list_fireball.append(new_fb)
        boss_cool.a_attack = randint(20, 80)
    if boss_cool.a_attack > 0:
        boss_cool.a_attack -= 1
    if phase_boss == 1:
        for ball in list_fireball[:]:
            if detection_joueur() == True:
                ball.pos_x += 12
            else:
                ball.pos_x -= 12
            if hitbox(player, ball) == True:
                player.health = player.health - 10
                list_fireball.remove(ball)
                continue
            if ball.pos_x < -10:
                list_fireball.remove(ball)

    if phase_boss == 2:
        for ball in list_fireball[:]:
            ball.pos_y += 12
            if hitbox(player, ball) == True:
                player.health = player.health - 10
                list_fireball.remove(ball)
                continue
            if ball.pos_y > LOG_H:
                list_fireball.remove(ball)


def change_phase():
    global phase_boss, is_fireball_rotated, fireball_sprite
    if boss.health == 1000:
        phase_boss = 1
    elif boss.health <= 500:
        if not is_fireball_rotated:
            is_fireball_rotated = True
            fireball_sprite = pygame.transform.rotate(fireball_sprite, 90)
        phase_boss = 2


def detection_joueur():
    if player.pos_x < boss.pos_x:
        return False
    else:
        return True


def phase_vol():
    if phase_boss == 2:
        boss.pos_y = 100


def player_arrow_2():
    global double_arrow_timer, double_arrow
    if double_arrow_timer > 0:
        double_arrow_timer -= 1
        if double_arrow_timer == 0:
            double_arrow = False


def deplacement_boss():
    if phase_boss == 1:
        if detection_joueur() == True:
            boss.pos_x -= 4
        else:
            boss.pos_x += 4
    if phase_boss == 2:
        if detection_joueur() == True:
            boss.pos_x += 24
        else:
            boss.pos_x -= 24


def boss_spikes():
    if boss_cool.b_attack <= 0 and phase_boss == 1:
        for i in range(1, 100):
            if i % 2 == 0:
                new_spike = entity(boss.pos_x + (40 * i), boss.pos_y + 50*i, 20, 200, 1, 0, 0, 1)
            else:
                new_spike = entity(boss.pos_x - (40 * i), boss.pos_y + 50*i, 20, 200, 1, 0, 0, 1)
            list_spike.append(new_spike)
            boss_cool.b_attack = randint(500, 700)
    for spike in list_spike:
        if spike.g == 1:
            spike.pos_y -= 6
        else:
            spike.pos_y += 6
        if spike.pos_y < H - 200:
            spike.g = 0
        if hitbox(player, spike) == True:
            player.health = player.health - 10
            list_spike.remove(spike)
        if boss.pos_y > 2*H:
            list_spike.remove(spike)
    if boss_cool.b_attack > 0:
        boss_cool.b_attack -= 1


def consumable():
    if consumable_cool.a_attack <= 0:
        new_consumable = entity(randint(10, LOG_W - 40), 0, 40, 40, 0, 0, 0, 1)
        list_consumable.append(new_consumable)
        consumable_cool.a_attack = randint(1200, 3600)
    if consumable_cool.a_attack > 0:
        consumable_cool.a_attack -= randint(1, 25)
    for new_consumable in list_consumable:
        new_consumable.pos_y += 7
        if hitbox(player, new_consumable):
            list_consumable.remove(new_consumable)
            player.health += 5
        floor_limit = LOG_H - 40
        if new_consumable.pos_y + new_consumable.y >= floor_limit:
            list_consumable_fixe.append(new_consumable)
            list_consumable.remove(new_consumable)
        for new_con in list_consumable_fixe:
            if hitbox(player, new_con):
                list_consumable_fixe.remove(new_con)
                num_con = randint(1, 3)
                if num_con == 1:
                    player.health += 20
                elif num_con == 2:
                    global double_arrow, double_arrow_timer
                    double_arrow = True
                    double_arrow_timer = 180
                elif num_con == 3:
                    boss.health -= 100

def draw_game():
    global img_sprite_boss
    sprite_player = sprite_player_choice()

    logical_screen.fill(noir)
    logical_screen.blit(background, (0, 0))
    logical_screen.blit(sprite_player, (player.pos_x - 40, player.pos_y - 80))
    logical_screen.blit(img_sprite_boss, (boss.pos_x - 120, boss.pos_y - 120))

    if player_cool.plat > 180:
        pygame.draw.rect(logical_screen, bleue, (plat.pos_x, plat.pos_y, plat.x, plat.y))
    pygame.draw.rect(logical_screen, rouge, (100, 50, boss.health, 40))
    pygame.draw.rect(logical_screen, vert, (140, 100, player.health * 8, 40))

    for ball in list_fireball:
        logical_screen.blit(fireball_sprite, (ball.pos_x, ball.pos_y))
    for arrow in list_arrow:
        logical_screen.blit(arrow_sprite, (arrow.pos_x, arrow.pos_y))
    for new_spike in list_spike:
        pygame.draw.rect(logical_screen, marron, (new_spike.pos_x, new_spike.pos_y, new_spike.x, new_spike.y))

    x, y = get_mouse_pos()
    dx = x - (player.pos_x + 8)
    dy = y - (player.pos_y + 16)
    distance = math.hypot(dx, dy)
    if distance != 0:
        speed = 30
        vel_x = (dx / distance) * speed
        vel_y = (dy / distance) * speed
    else:
        vel_x = 0
        vel_y = 0
    start_x = player.pos_x + 8
    start_y = player.pos_y + 16
    points = get_trajectory_points(start_x, start_y, vel_x, vel_y)
    for i in range(1, len(points)):
        pygame.draw.line(logical_screen, rouge, points[i - 1], points[i], 2)

    for new_con in list_consumable:
        logical_screen.blit(img_consumable, (new_con.pos_x, new_con.pos_y))
    for new_con in list_consumable_fixe:
        logical_screen.blit(img_consumable, (new_con.pos_x, new_con.pos_y))

    if phase_boss == 2:
        title = font_title.render("THE BOSS IS ANGRY", True, blanc)
        shadow = font_title.render("THE BOSS IS ANGRY", True, noir)
        logical_screen.blit(shadow, (LOG_W // 2 - title.get_width() // 2 + 3, 163))
        logical_screen.blit(title, (LOG_W // 2 - title.get_width() // 2, 160))

    scaled_surface = pygame.transform.scale(logical_screen, (W, H))
    screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()


def update_game():
    global double_arrow_timer, double_arrow
    keys = pygame.key.get_pressed()
    phase_vol()
    jump(keys)
    gravity()
    moove(keys)
    debug(boss)
    debug(player)
    temp_plat(keys)
    boss_gravity()
    boss_fireball()
    deplacement_boss()
    detection_joueur()
    change_phase()
    player_arrow(keys)
    boss_spikes()
    consumable()
    player_arrow_2()

    if player.health <= 0:
        print("Game Over")
        pygame.quit()
        sys.exit()
    if boss.health <= 0:
        print("You Win!")
        pygame.draw.rect(screen, vert, (0, 0, W, H))
        title = font_title.render("Jeu ?, You WON !", True, blanc)
        shadow = font_title.render("Jeu ?, You WON !", True, noir)
        screen.blit(shadow, (W // 2 - title.get_width() // 2 + 3, 103))
        screen.blit(title, (W // 2 - title.get_width() // 2, 100))
        pygame.display.flip()
        wait_time = pygame.time.get_ticks() + 2000
        while pygame.time.get_ticks() < wait_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.flip()
        pygame.quit()
        sys.exit()


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    update_game()

    if running:
        draw_game()

    clock.tick(FPS)

pygame.quit()
sys.exit()