import pygame as pg

from .. import pg_init, pg_root

from .. components import colors
from .. interface import button


class Neuro(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.next = "GAME"
        self.sim_ref_state = (0.5, 0)
        self.sim_init_state = (0, 0, 0, 0.3)

        self.but_set = button.Button('Settings', colors.LBLUE, colors.WHITE)
        self.but_set.set_pos(self.width-self.but_set.width-15, 10)

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.next = "GAME"

        if self.previous is not 'SPLASH':
            self.sim_ref_state = self.persist["sim reference state"]
            self.sim_init_state = self.persist["sim initial state"]

    def cleanup(self):
        self.done = False
        self.persist["sim reference state"] = self.sim_ref_state
        self.persist["sim initial state"] = self.sim_init_state
        self.persist["bg_image"] = self.screenshot_imagestr
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
            if event.key == pg.K_BACKSPACE:
                self.next = "SPLASH"
                self.done = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            pass

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.but_set.mouseover:
                self.next = "SETTINGS"
                self.done = True

    def mouse_logic(self, mouse):
        self.hover_object_logic(mouse, self.but_set)

    def update(self, surface):
        self.screenshot_imagestr = pg.image.tostring(surface, 'RGB')
        self.draw(surface)

    def draw(self, surface):
        surface.fill(colors.WHITE)
        self.draw_interface(surface)

    def draw_interface(self, surface):
        self.draw_button(surface, self.but_set)
