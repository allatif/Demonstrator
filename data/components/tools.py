import pygame as pg


def draw_aafilled_polygon(surface, points, color):
    pg.gfxdraw.aapolygon(surface, points, color)
    pg.gfxdraw.filled_polygon(surface, points, color)


def draw_aafilled_circle(surface, x, y, r, color):
    pg.gfxdraw.aacircle(surface, x, y, r, color)
    pg.gfxdraw.filled_circle(surface, x, y, r, color)


def draw_aafilled_ring(surface, x, y, r, w, color):
    pg.gfxdraw.aacircle(surface, x, y, r-w-1, color)
    pg.gfxdraw.aacircle(surface, x, y, r-w, color)
    pg.gfxdraw.aacircle(surface, x, y, r-1, color)
    pg.gfxdraw.aacircle(surface, x, y, r, color)
    pg.draw.circle(surface, color, (x, y), r, w)
