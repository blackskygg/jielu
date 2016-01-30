# -*- coding: utf-8 -*-
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlgfx import *
from sdl2.sdlttf import *
import os

#Initialization
SDL_Init(SDL_INIT_EVERYTHING)
IMG_Init(IMG_INIT_PNG | IMG_INIT_JPG)
TTF_Init()
font1 = TTF_OpenFont("xingshu.ttf".encode(), 100)

#TEST
#SDL_Delay(6000)

#create a full-screen window with screenshot
os.system("scrot -z shot.png".encode())
background = IMG_Load("shot.png".encode())

disp_rect = SDL_Rect()
SDL_GetDisplayBounds(0, disp_rect)
win = SDL_CreateWindow("Blue".encode(), disp_rect.x, disp_rect.y, disp_rect.w, disp_rect.h, SDL_WINDOW_FULLSCREEN_DESKTOP)
surface = SDL_GetWindowSurface(win)
SDL_BlitSurface(background, None, surface, None)
SDL_UpdateWindowSurface(win)

SDL_Delay(1000)

#display an img
#img = IMG_Load("flower.png")
img = TTF_RenderUTF8_Solid(font1, "呵呵呵呵".encode(), SDL_Color(0, 0, 0))
rect = SDL_Rect(0, int(disp_rect.h/2 - img.contents.h/2), img.contents.w, img.contents.h)
rect2 = rect.__copy__()
for i in range(int((disp_rect.w - img.contents.w)/2), disp_rect.w - img.contents.w):
    SDL_BlitSurface(background, rect, surface, rect)
    SDL_BlitSurface(background, rect2, surface, rect2)
    rect.x = i
    rect2.x = disp_rect.w - i - img.contents.w
    SDL_BlitSurface(img, None, surface, rect)
    SDL_BlitSurface(img, None, surface, rect2)
    SDL_UpdateWindowSurface(win)
    SDL_Delay(10)

