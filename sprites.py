# Written (with love) by Lex Whalen

import pygame as pg

class LineSprite():

    def __init__(self,surf,x,y,w,h,dx,color):
        pg.init()
        self.SURF = surf
        self.X = x
        self.Y = y
        self.W = w
        self.H = h
        self.COLOR = color
        self.DX = dx

        self.RECT  = pg.Rect(self.X,self.Y,self.W,self.H)
    
    def draw(self):
        pg.draw.rect(self.SURF,self.COLOR,self.RECT)

    def update(self):
        self.RECT.x += self.DX
        self.draw()

    def set_dx(self,dx):
        self.DX = dx 

    def reset_line(self):
        self.RECT.x = self.X

    
