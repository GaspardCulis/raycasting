"""
Raycasting

Coordds be like : for 16*11 map : (3.14, 1.414)

"""
import pygame
from time import *
from random import *
import numpy as np
from PIL import Image
from math import *

screen_size = (1080, 720)
texture_size = (16, 16)
sprite_size = (32, 32)

pygame.init()
screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
pygame.display.set_caption('WAW')
pygame.mouse.set_visible(0)


def IT(path):  # Stands for Import Texture
    return np.rot90(np.asarray(Image.open("resources/"+path)))


class spriteSheet():
    def __init__(self, image_path, rows, scale=1):
        self.frames = list()
        self.sheet = pygame.image.load("resources/"+image_path).convert_alpha()
        self.rows = rows
        self.frame_width, self.frame_height = self.sheet.get_size()
        self.frame_width /= rows
        for i in range(self.rows):
            frame = self.sheet.subsurface(pygame.Rect(
                i*self.frame_width, 0, self.frame_width, self.frame_height))
            scaled = (int(np.multiply(frame.get_size(), scale)[0]),
                      int(np.multiply(frame.get_size(), scale)[1]))
            frame = pygame.transform.scale(frame, scaled)
            self.frames.append(frame)


pistol = spriteSheet("pistol_spritesheet.png", 19,
                     scale=0.8 * screen_size[1]/720)


textures = [IT("stone_wall.png"), IT("broken_stone_wall.png"),
            IT("mossy_stone_wall.png"), IT("void.png")]

map_size = (16, 11)

Map = np.array([[1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 1, 0, 3, 2, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 3, 3, 0, 0, 1, 0, 0, 0, 0, 1],
                [1, 1, 2, 3, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 2, 1, 1]])

player_x = 1.5
player_y = 1.5
player_angle = 0

colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]


def AIE(x, y):  # Stands for Avoid Indexing Errors
    new_x, new_y = max(min(x, len(Map[0])-1), 0), max(min(y, len(Map)-1), 0)
    return new_x, new_y, new_x != x or new_y != y


def cast_ray(x, y, angle, sprites):
    V_d, H_d = 1000, 1000
    # Horizontal
    H_first_x, H_first_y, H_xStep, H_yStep = 0, 0, 0, 0
    if sin(angle):
        if sin(angle) > 0:
            H_first_y = np.ceil(y)-y  # + 0.1
            H_y_modifier = 0.1
            H_yStep = 1
        else:
            H_first_y = int(y)-y  # - 0.1
            H_y_modifier = -0.1
            H_yStep = -1
        H_first_x = H_first_y/tan(angle)
        H_xStep = 1/tan(H_yStep*angle)

        for H_d in range(2048):
            H_x, H_y = x+H_first_x + H_xStep*H_d, y+H_first_y + H_yStep*H_d
            H_mx, H_my, changed = AIE(int(H_x), int(H_y+H_y_modifier))
            #fill_rect((x+H_first_x + H_xStep*H_d)*size_x -2, (y+H_y_modifier+H_first_y + H_yStep*H_d)*size_y -2, 4, 4, (255,255,0))
            H_map_value = Map[H_my, H_mx]
            if H_map_value or changed:
                H_d = np.sqrt((H_first_x + H_xStep*H_d)**2 +
                              (H_first_y + H_yStep*H_d)**2)
                break
    # Vertical
    V_first_x, V_first_y, V_xStep, V_yStep = 0, 0, 0, 0
    if cos(angle):
        if cos(angle) > 0:
            V_first_x = np.ceil(x)-x  # + 0.1
            V_x_modifier = 0.1
            V_xStep = 1
        else:
            V_first_x = int(x)-x  # - 0.1
            V_x_modifier = -0.1
            V_xStep = -1
        V_first_y = V_first_x*tan(angle)
        V_yStep = tan(V_xStep*angle)

        for V_d in range(2048):
            V_x, V_y = x+V_x_modifier + V_xStep*V_d, y+V_first_y + V_yStep*V_d
            V_mx, V_my, changed = AIE(int(V_x+V_first_x), int(V_y))
            #fill_rect((x+V_x_modifier+V_first_x + V_xStep*V_d)*size_x -2, (y+V_first_y + V_yStep*V_d)*size_y -2, 4, 4, (0,255,255))
            V_map_value = Map[V_my, V_mx]
            if V_map_value or changed:
                V_d = np.sqrt((V_first_x + V_xStep*V_d)**2 +
                              (V_first_y + V_yStep*V_d)**2)
                break
    # Sprites
    sprites_textures_y, sprites_distances = list(), list()
    for s in sprites:
        # angle to player view
        atpv = -atan2(s.position[1] - y, s.position[0] - x) + angle
        if degrees(atpv + 2*pi) % 360 > FOV/2 - 10 and degrees(atpv + 2*pi) % 360 < 360 - FOV/2 + 10:
            continue
        # Distance to player
        dtp = np.sqrt((x-s.position[0])**2 + (y-s.position[1])**2)
        dtsc = tan(atpv)*dtp  # distance_to_sprite_center
        dtsc /= abs(cos(s.direction + atpv - angle))
        if abs(dtsc) > 0.5:
            continue
        sprites_distances.append(dtp)
        if cos(s.direction + atpv - angle) < 0:
            sprites_textures_y.append(
                s.front_texture[int((dtsc + 0.5)*sprite_size[0])])
        else:
            sprites_textures_y.append(
                s.back_texture[int((dtsc + 0.5)*sprite_size[0])])
    sprites_textures_y = [sprites_textures_y for sprites_distances,
                          sprites_textures_y in sorted(zip(sprites_distances, sprites_textures_y))]
    sprites_textures_y.reverse()
    sprites_distances = sorted(sprites_distances)
    sprites_distances.reverse()
    # Return
    distance = min(V_d, H_d)
    if distance == H_d:
        if sin(angle) > 0:
            x_offset = H_x - int(H_x)
        else:
            x_offset = np.ceil(H_x) - H_x
        return distance, np.multiply(textures[H_map_value - 1][int(x_offset*texture_size[0])], 0.6), sprites_distances, sprites_textures_y
    else:
        if cos(angle) < 0:
            y_offset = V_y - int(V_y)
        else:
            y_offset = np.ceil(V_y) - V_y
        return distance, textures[V_map_value - 1][int(y_offset*texture_size[1])], sprites_distances, sprites_textures_y


def transform(ray, angle):  # Avoid fisheye effect
    return np.multiply(np.cos(angle), ray)


def render(distance, texture_column, sprites_distance, sprites_textures_y, x):
    # Render walls
    ray_height = (300*screen_size[1]/222)/distance
    a = max(min(1-distance/20, 1), 0)
    pixel_height = ray_height/len(texture_column)
    texture_column = np.multiply(texture_column, a)
    for t in range(len(texture_column)):
        pygame.draw.rect(screen, texture_column[t], (x*ray_width, screen_size[1]/2 - pixel_height*(
            texture_size[1]/2) + t*pixel_height, ray_width+1, pixel_height+1))
    # Render Sprites
    for d, t in zip(sprites_distances, sprites_textures_y):
        if d != -1 and d < distance:
            sprite_height = (300*screen_size[1]/222)/d
            T = np.multiply(t, max(min(1-d/20, 1), 0))
            pixel_height = sprite_height/len(t)
            for i in range(len(t)):
                if T[i][2]:
                    pygame.draw.rect(screen, T[i], (x*ray_width, screen_size[1]/2 - pixel_height*(
                        sprite_size[1]/2) + i*pixel_height, ray_width+1, pixel_height+1))


class Sprite():
    def __init__(self, position, front_texture, back_texture, direction=0):
        self.position, self.direction = position, direction
        self.front_texture, self.back_texture = front_texture, back_texture


Sprites = [Sprite([2.5, 4.5], IT("ennemy_front.png"), IT("ennemy_back.png")),
           Sprite([3, 4.5], IT("ennemy_front.png"), IT("ennemy_back.png"))]


delta = 0

size_x, size_y = 0, 0

FOV = 60
detail = 5

ray_width = screen_size[0]/(FOV*detail)

RIGHT, LEFT, UP, DOWN = False, False, False, False

ennemy = Sprites[0]
ennemy_direction = -1

old_mouse_pos = pygame.mouse.get_pos()

mouse_pass = 1

fpss = list()

while 1:
    # Controls
    t0 = monotonic()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                LEFT = True
            if event.key == pygame.K_d:
                RIGHT = True
            if event.key == pygame.K_z:
                UP = True
            if event.key == pygame.K_s:
                DOWN = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_q:
                LEFT = False
            if event.key == pygame.K_d:
                RIGHT = False
            if event.key == pygame.K_z:
                UP = False
            if event.key == pygame.K_s:
                DOWN = False
        if event.type == pygame.VIDEORESIZE:
            print("toto")
            screen_size = screen.get_size()
            ray_width = screen_size[0]/(FOV*detail)

    if player_angle >= 2*pi:
        player_angle -= 2*pi
    if player_angle < 0:
        player_angle += 2*pi
    if UP:
        if not Map[int(player_y + sin(player_angle)*0.5), int(player_x + cos(player_angle)*0.5)]:
            player_x += 2*cos(player_angle)*delta
            player_y += 2*sin(player_angle)*delta
    if DOWN:
        if not Map[int(player_y - sin(player_angle)*0.5), int(player_x - cos(player_angle)*0.5)]:
            player_x -= 2*cos(player_angle)*delta
            player_y -= 2*sin(player_angle)*delta
    if RIGHT:
        if not Map[int(player_y + sin(player_angle+pi/2)*0.5), int(player_x + cos(player_angle+pi/2)*0.5)]:
            player_x += cos(player_angle+pi/2)*delta
            player_y += sin(player_angle+pi/2)*delta
    if LEFT:
        if not Map[int(player_y - sin(player_angle+pi/2)*0.5), int(player_x + cos(player_angle+pi/2)*0.5)]:
            player_x -= cos(player_angle+pi/2)*delta
            player_y -= sin(player_angle+pi/2)*delta
    mouse_pos = pygame.mouse.get_pos()
    player_angle += pi*delta*(mouse_pos[0]-old_mouse_pos[0])/10 * mouse_pass
    old_mouse_pos = mouse_pos
    mouse_pass = 1
    if abs(mouse_pos[0] - screen_size[0]/2) > screen_size[0]/2*0.8 or abs(mouse_pos[1] - screen_size[1]/2) > screen_size[1]/2*0.8:
        mouse_pass = 0
        pygame.mouse.set_pos(np.divide(screen_size, 2))

    # Render
    pygame.draw.rect(screen, (89, 87, 87),
                     (0, 0, screen_size[0], screen_size[1]/2))
    pygame.draw.rect(screen, (0, 255, 0),
                     (0, screen_size[1]/2, screen_size[0], screen_size[1]/2))

    for m in range(int(-FOV*detail/2), int(FOV*detail/2)):
        distance, texture_column, sprites_distances, sprites_textures_y = cast_ray(
            player_x, player_y, player_angle + radians(m/detail), Sprites)
        render(transform(distance, radians(m/detail)), texture_column, transform(
            sprites_distances, radians(m/detail)), sprites_textures_y, m + int(FOV*detail/2))
    # Pistol
    screen.blit(pistol.frames[0], np.subtract(
        screen_size, pistol.frames[0].get_size()))

    if delta != 0:
        fpss.append(1/np.clip(delta, 1e-7, 1e7))

    if len(fpss) > 60:
        print("On 60 frames , got {}fps average.".format(
            round(sum(fpss)/len(fpss), 2)))
        fpss = list()

    pygame.display.flip()

    # Ennemy behavior
    Sprites[1].position[1] += ennemy_direction*delta
    if not(1.5 < Sprites[1].position[1] and Sprites[1].position[1] < 11):
        ennemy_direction *= -1

    ennemy.position[0] += cos(ennemy.direction)*delta
    ennemy.position[1] += sin(ennemy.direction)*delta
    if Map[int(ennemy.position[1] + sin(ennemy.direction)), int(ennemy.position[0] + cos(ennemy.direction))]:
        ennemy.direction += 2*pi*delta

    delta = monotonic()-t0
