import math as m

import pygame as pg
import pygame.gfxdraw


from .. import pg_init, pg_root, setup_sim

from .. components import color
from .. interface import window, slider, button


class SetMenu(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.box = window.MenuWindow()
        self.next = "POLEMAP"

        self.but_ok = button.Button('OK', color.LRED, color.LLRED, color.WHITE)

        self.head_font = pg.font.SysFont('Liberation Sans', 26)

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.bg_img = pg.image.fromstring(self.persist["bg_image"],
                                          (self.width, self.height), 'RGB')

    def cleanup(self):
        self.done = False
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            pass

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            pass

    def update(self, surface):
        self.draw(surface)

    def draw(self, surface):
        surface.blit(self.bg_img, pg_init.SCREEN_RECT)
        pg.gfxdraw.box(surface, self.box.rect, color.TRAN225)

        self.draw_heading(surface)
        self.draw_button(surface, self.but_ok)

    def draw_heading(self, surface):
        text_str = 'Settings Menu'
        text = self.head_font.render(text_str, True, color.WHITE)
        surface.blit(text, self.box.con_pos)

    @staticmethod
    def deg2rad(deg):
        return deg * (m.pi/180)

    @staticmethod
    def rad2deg(rad):
        return (rad*180) / m.pi
