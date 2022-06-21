"""
Raycasting

Coordds be like : for 16*11 map : (3.14, 1.414)

"""
import pygame
from time import *
from random import *
import numpy as np
import PIL
from PIL import Image
from math import *

screen_size = (1080, 720)
texture_size = (16, 16)
sprite_size = (32, 32)

pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('WAW')


def IT(path):  # Stands for Import Texture
    return np.rot90(np.asarray(PIL.Image.open("resources/"+path)))


stone_wall = Image.open("resources/stone_wall.png")
broken_stone_wall = Image.open("resources/broken_stone_wall.png")
mossy_stone_wall = Image.open("resources/mossy_stone_wall.png")


textures = [IT("stone_wall.png"), IT("broken_stone_wall.png"),
            IT("mossy_stone_wall.png"), IT("void.png")]

sprite_textures = [IT("ennemy_front.png")]

map_size = (16, 11)

Map = np.array([[1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1],
                [1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 3, 2, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 3, 0, 3, 3, 0, 0, 1, 0, 0, 0, 0, 1],
                [1, 1, 2, 3, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 3, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 2, 1, 1]])

player_x = 1.5
player_y = 1.5
player_angle = 0

colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]


def AIE(x, y):  # Stands for Avoid Indexing Errors
    new_x, new_y = max(min(x, len(Map[0])-1), 0), max(min(y, len(Map)-1), 0)
    return new_x, new_y, new_x != x or new_y != y


def cast_ray(x, y, angle):
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
    distance = min(V_d, H_d)
    if distance == V_d:
        return distance, V_x, V_y, V_map_value, "V"
    else:
        return distance, H_x, H_y, H_map_value, "H"


def cast_rays(x, y, angle, FOV, detail, sprites):
    distances, texture_columns, sprite_distances, sprite_columns = list(), list(), list(), list()
    for m in range(int(-FOV*detail/2), int(FOV*detail/2)):
        # Walls
        a = angle + radians(m/detail)
        d, hit_x, hit_y, map_value, Type = cast_ray(x, y, a)
        if Type == "H":
            if sin(a) > 0:
                x_offset = hit_x - int(hit_x)
            else:
                x_offset = np.ceil(hit_x) - hit_x
            texture_column = np.multiply(
                textures[map_value - 1][int(x_offset*texture_size[0])], 0.6)
        else:
            if cos(a) < 0:
                y_offset = hit_y - int(hit_y)
            else:
                y_offset = np.ceil(hit_y) - hit_y
            texture_column = textures[map_value -
                                      1][int(y_offset*texture_size[1])]
        distances.append(transform(d, radians(m/detail)))
        texture_columns.append(texture_column)
        # Sprites
        for s in sprites:
            # angle to player view
            atpv = -atan2(s.position[1] - y, s.position[0] - x) + angle
            if not abs(degrees(atpv)) < FOV/2:
                # print("nope")
                pass
            else:
                # print("yes")
                pass
            # Distance to player
            dtp = np.sqrt((x-s.position[0])**2 + (y-s.position[1])**2)
            dtsc = tan(atpv)*dtp  # distance_to_sprite_center

    return distances, texture_columns, sprite_distances, sprite_columns


def transform(ray, angle):  # Avoid fisheye effect
    return cos(angle)*ray


def tridi_render(rays, texture_columns, sprites_distances, sprite_columns):
    pygame.draw.rect(screen, (89, 87, 87),
                     (0, 0, screen_size[0], screen_size[1]/2))
    pygame.draw.rect(screen, (0, 255, 0),
                     (0, screen_size[1]/2, screen_size[0], screen_size[1]/2))
    ray_width = screen_size[0]/len(rays)
    for r in range(len(rays)):
        ray_height = (300*screen_size[1]/222)/rays[r]
        a = max(min(1-rays[r]/20, 1), 0)
        texture_column = np.multiply(texture_columns[r], a)
        pixel_height = ray_height/len(texture_column)
        # Render walls
        for t in range(len(texture_column)):
            temp = t*pixel_height
            pygame.draw.rect(screen, texture_column[t], (r*ray_width, screen_size[1]/2 - pixel_height*(
                texture_size[1]/2) + temp, ray_width+1, pixel_height+1))


class Sprite():
    def __init__(self, position, texture):
        self.position, self.texture = position, texture


Sprites = [Sprite((12.5, 8.5), sprite_textures[0])]


delta = 0

size_x, size_y = 0, 0

font = pygame.font.SysFont(None, 32)

FOV, detail = 60, 5

RIGHT, LEFT, UP, DOWN = False, False, False, False

while 1:
    t0 = monotonic()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                LEFT = True
            if event.key == pygame.K_RIGHT:
                RIGHT = True
            if event.key == pygame.K_UP:
                UP = True
            if event.key == pygame.K_DOWN:
                DOWN = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                LEFT = False
            if event.key == pygame.K_RIGHT:
                RIGHT = False
            if event.key == pygame.K_UP:
                UP = False
            if event.key == pygame.K_DOWN:
                DOWN = False

    distances, texture_columns, sprites_distances, sprite_columns = cast_rays(
        player_x, player_y, player_angle, FOV, detail, Sprites)

    tridi_render(distances, texture_columns, sprites_distances, sprite_columns)

    if RIGHT:
        player_angle += pi/2*delta
    if LEFT:
        player_angle -= pi/2*delta
    if player_angle >= 2*pi:
        player_angle -= 2*pi
    if player_angle < 0:
        player_angle += 2*pi
    if UP and not Map[int(player_y + sin(player_angle)*0.5), int(player_x + cos(player_angle)*0.5)]:
        player_x += 2*cos(player_angle)*delta
        player_y += 2*sin(player_angle)*delta
    if DOWN and not Map[int(player_y - sin(player_angle)*0.5), int(player_x - cos(player_angle)*0.5)]:
        player_x -= 2*cos(player_angle)*delta
        player_y -= 2*sin(player_angle)*delta
    img = font.render(str(round(1/np.clip(delta, 1e-7, 1e7))), True, (0, 0, 0))
    screen.blit(img, (0, 0))
    pygame.display.flip()
    delta = monotonic()-t0
