"""
Raycasting

Coordds be like : for 16*11 map : (3.14, 1.414)

"""
from math import *
from kandinsky import *
from time import *
from random import *
from ion import *

screen_size = (320, 222)
map_size = (16, 11)

Map = [[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
       [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
       [1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
       [2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
       [1, 0, 2, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 2],
       [2, 0, 0, 0, 0, 0, 3, 3, 0, 0, 1, 0, 0, 0, 0, 1],
       [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 2],
       [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
       [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 0, 1, 0, 2],
       [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
       [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]]

player_x = 1.5
player_y = 1.5
player_angle = 0

colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]


def AIE(x, y):  # Stands for Avoid Indexing Errors
    return max(min(x, map_size[0]-1), 0), max(min(y, map_size[1]-1), 0)


def list_multiply(List, number):
    out = list()
    for i in List:
        out.append(i*number)
    return out


def draw_map_top_view():
    fill_rect(0, 0, map_size[0], map_size[1], (50, 50, 50))
    for i in range(map_size[0]):
        for j in range(map_size[1]):
            size_x, size_y = screen_size[0] / \
                map_size[0], screen_size[1]/map_size[1]
            fill_rect(int(i*size_x + 1), int(j*size_y + 1),
                      int(size_x - 2), int(size_y - 2), colors[Map[j][i]])
    fill_rect(int(player_x*size_x)-2,
              int(player_y*size_y)-2, 4, 4, (255, 0, 0))
    return size_x, size_y


def cast_ray(x, y, angle):
    V_d, H_d = 1000, 1000
    # Horizontal
    H_first_x, H_first_y, H_xStep, H_yStep = 0, 0, 0, 0
    if sin(angle):
        if sin(angle) > 0:
            H_first_y = ceil(y)-y  # + 0.1
            H_y_modifier = 0.1
            H_yStep = 1
        else:
            H_first_y = int(y)-y  # - 0.1
            H_y_modifier = -0.1
            H_yStep = -1
        H_first_x = H_first_y/tan(angle)
        H_xStep = 1/tan(H_yStep*angle)

        out_of_map = False
        for H_d in range(100):
            H_mx, H_my = AIE(
                int(x+H_first_x + H_xStep*H_d), int(y+H_y_modifier+H_first_y + H_yStep*H_d))
            #fill_rect((x+H_first_x + H_xStep*H_d)*size_x -2, (y+H_y_modifier+H_first_y + H_yStep*H_d)*size_y -2, 4, 4, (255,255,0))
            if Map[H_my][H_mx]:
                H_d = sqrt((H_first_x + H_xStep*H_d)**2 +
                           (H_first_y + H_yStep*H_d)**2)
                break
    # Vertical
    V_first_x, V_first_y, V_xStep, V_yStep = 0, 0, 0, 0
    if cos(angle):
        if cos(angle) > 0:
            V_first_x = ceil(x)-x  # + 0.1
            V_x_modifier = 0.1
            V_xStep = 1
        else:
            V_first_x = int(x)-x  # - 0.1
            V_x_modifier = -0.1
            V_xStep = -1
        V_first_y = V_first_x*tan(angle)
        V_yStep = 1*tan(V_xStep*angle)

        for V_d in range(100):
            V_mx, V_my = AIE(
                int(x+V_x_modifier+V_first_x + V_xStep*V_d), int(y+V_first_y + V_yStep*V_d))
            #fill_rect((x+V_x_modifier+V_first_x + V_xStep*V_d)*size_x -2, (y+V_first_y + V_yStep*V_d)*size_y -2, 4, 4, (0,255,255))
            if Map[V_my][V_mx]:
                V_d = sqrt((V_first_x + V_xStep*V_d)**2 +
                           (V_first_y + V_yStep*V_d)**2)
                break
    distance = min(V_d, H_d)
    if distance == V_d:
        return distance, colors[Map[V_my][V_mx]]
    else:
        return distance, list_multiply(colors[Map[H_my][H_mx]], 0.6)


def transform(ray, angle):  # Avoid fisheye effect
    return cos(angle)*ray


def tridi_render(rays, cols):
    fill_rect(0, 0, screen_size[0], int(screen_size[1]/2), (0, 255, 255))
    fill_rect(0, int(screen_size[1]/2), screen_size[0],
              int(screen_size[1]/2), (0, 255, 0))
    ray_width = screen_size[0]/len(rays)
    for r in range(len(rays)):
        ray_height = (max(len(Map), len(Map[0]))-rays[r])**2
        ray_height = (250*screen_size[1]/222)/rays[r]
        a = max(min(1-rays[r]/10, 1), 0)
        col = (int(cols[r][0]*a), int(cols[r][1]*a), int(cols[r][2]*a))
        #col = cols[r]
        fill_rect(int(r*ray_width),
                  int(screen_size[1]/2 - ray_height/2), int(ray_width)+1, int(ray_height), col)


delta = 0

size_x, size_y = 0, 0

while 1:
    t0 = monotonic()
    if keydown(KEY_OK):
        size_x, size_y = draw_map_top_view()
    #fill_rect(size_x*(player_x + cos(player_angle)*3) -1, size_y*(player_y + sin(player_angle)*3) -1, 2, 2, (0,255,0))
    rays = list()
    cols = list()
    for i in range(-300, 300):
        d, col = cast_ray(player_x, player_y, player_angle+radians(i/10))
        d = transform(d, radians(i/10))
        rays.append(d)
        cols.append(col)
        if keydown(KEY_OK):
            fill_rect(int(size_x*(player_x + cos(player_angle+radians(i/10))*d) - 2),
                      int(size_y*(player_y + sin(player_angle+radians(i/10))*d) - 2), 4, 4, col)
    if not keydown(KEY_OK) and False:
        tridi_render(rays, cols)
    check_window_closing()
    if keydown(KEY_RIGHT):
        player_angle += pi/2*delta
    if keydown(KEY_LEFT):
        player_angle -= pi/2*delta
    if player_angle >= 2*pi:
        player_angle -= 2*pi
    if player_angle <= 0:
        player_angle += 2*pi
    if keydown(KEY_UP) and not Map[int(player_y + sin(player_angle)*0.5)][int(player_x + cos(player_angle)*0.5)]:
        player_x += 2*cos(player_angle)*delta
        player_y += 2*sin(player_angle)*delta
    if keydown(KEY_DOWN) and not Map[int(player_y - sin(player_angle)*0.5)][int(player_x - cos(player_angle)*0.5)]:
        player_x -= 2*cos(player_angle)*delta
        player_y -= 2*sin(player_angle)*delta
    delta = monotonic()-t0
    draw_string(str(int(1/delta))+"fps", 0, 0)
