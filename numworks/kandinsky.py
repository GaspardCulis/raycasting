# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 10:29:31 2021

@author: gaspa
"""
import pygame

#Pygame init
pygame.init()
screen_size=(1080,720)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Numworks')

def check_window_closing():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
def get_pixel(x,y):
    return (screen.get_at((x,y)))[0:3]

def set_pixel(x,y,color):
    screen.set_at((x,y),color)
    pygame.display.flip()
    
def fill_rect(x,y,width,height,color):
    pygame.draw.rect(screen,color,(x,y,width,height))
    #pygame.display.flip()
    
def draw_string(text,x,y,text_color=(0,0,0),background_color=(255,255,255)):
    font = pygame.font.Font('arial.ttf', 16)
    rendered_text = font.render(text, True, text_color, background_color)
    screen.blit(rendered_text, (x,y))
    pygame.display.flip()
    
def color(r,g,b):
    print("Not implemented yet.")
    return((r,g,b))