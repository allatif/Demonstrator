import math as m

import pygame as pg
import pygame.gfxdraw


from .. import pg_init, pg_root, setup_sim

from .. components import color
from .. interface import window, slider_group, slider, button


class SetupMenu(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.next = "POLEMAP"

        self.win = window.MenuWindow('Settings Menu')
        self.win.cache_font(self.win.header, 'Liberation Sans', 26, color.WHITE)

        # Initialize button
        self.but_ok = button.Button('OK', color.LRED, color.LLRED, color.WHITE)
        self.but_ok.set_pos(self.win.con_right-self.but_ok.width,
                            self.win.con_bottom-self.but_ok.height)

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        # self.sim_init_state = self.persist["sim initial state"]

        # Initialize sliders
        self.sliders = []
        slider_ranges = [(-2, 2), (-2, 2), (-10, 10), (-20, 20)]
        for slider_range, val in zip(slider_ranges, [0, 0, 0, 4]):
            self.sliders.append(slider.Slider(val, 4, 250,
                                              range_=slider_range, margin=25,
                                              track_color=color.WHITE,
                                              act_filled_color=color.LLGREEN,
                                              act_thumb_color=color.LGREEN,
                                              act_value_color=color.LGREEN))
        self.slider_group = slider_group.SliderGroup(self.sliders)
        self.slider_group.arrange(self.win.con_pos[0],
                                  self.win.con_pos[1]+75)

        self.bg_img = pg.image.fromstring(self.persist["bg_image"],
                                          (self.width, self.height), 'RGB')

    def cleanup(self):
        self.done = False
        # self.persist["sim initial state"] = self.sim_init_state
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            pass

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.but_ok.mouseover:
                self.done = True

    def mouse_logic(self, mouse):
        self.hover_object_logic(mouse, self.but_ok)

    def update(self, surface):
        self.draw(surface)

    def draw(self, surface):
        surface.blit(self.bg_img, pg_init.SCREEN_RECT)
        pg.gfxdraw.box(surface, self.win.rect, color.TRAN225)

        self.draw_heading(surface)
        self.draw_slider_group(surface, self.slider_group)
        self.draw_button(surface, self.but_ok)

    def draw_heading(self, surface):
        surface.blit(self.win.font_cache, self.win.con_pos)
