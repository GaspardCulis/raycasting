# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 11:42:09 2021

@author: gaspa
"""

import keyboard

KEY_LEFT = "left"
KEY_UP = "up"
KEY_DOWN = "down"
KEY_RIGHT = "right"
KEY_OK = "enter"
KEY_BACK = "echap"
KEY_BACKSPACE = "backspace"
KEY_HOME = "home"

"""
while 1:
    if keyboard.is_pressed(KEY_HOME):
        break
    print("toto")
"""
def keydown(k):
    return keyboard.is_pressed(k)
