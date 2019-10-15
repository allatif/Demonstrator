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
        self.win.cache_font(self.win.header, 'Liberation Sans', 32, color.WHITE)

        # Initialize button
        self.but_ok = button.Button('OK', color.LRED, color.LLRED, color.WHITE)
        self.but_ok.set_pos(self.win.con_right-self.but_ok.width,
                            self.win.con_bottom-self.but_ok.height)

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)

        self.sim_init_state = self.persist["sim initial state"]
        self._init_sliders()
        self.slider_group = slider_group \
            .SliderGroup(self.sliders, header_text='Initial Conditions',
                         header_size=26)
        self.slider_group.arrange(self.win.con_pos[0]+10,
                                  self.win.con_pos[1]+75)

        self.bg_img = pg.image.fromstring(self.persist["bg_image"],
                                          (self.width, self.height), 'RGB')

    def cleanup(self):
        self.done = False

        state = self.slider_group.get_values()
        self.persist["sim initial state"] = list(self._state_in_rad(state))
        return self.persist

    def _init_sliders(self):
        # Initialize sliders
        self.sliders = []
        slider_ranges = [(-2, 2), (-2, 2), (-10, 10), (-20, 20)]
        zipped = zip(slider_ranges, self.sim_init_state)
        units = ['m', 'm/s', '°', '°/s']
        for num, (slider_range, val) in enumerate(zipped):
            if num > 1:
                val = self.rad2deg(val)
            self.sliders.append(slider.Slider(val, 4, 250, unit=units[num],
                                              range_=slider_range, margin=25,
                                              track_color=color.GREY,
                                              act_filled_color=color.LLGREEN,
                                              act_thumb_color=color.LGREEN,
                                              act_value_color=color.LGREEN))

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for sldr in self.sliders:
                if sldr.thumb.mouseover:
                    sldr.thumb.grab()
                    break

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for sldr in self.sliders:
                if sldr.thumb.grabbed:
                    sldr.thumb.release()
                    break

            if self.but_ok.mouseover:
                self.done = True

    def mouse_logic(self, mouse):
        self.slider_group_logic(mouse, self.sliders)
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

    def _state_in_rad(self, state):
        for num, value in enumerate(state):
            if num > 1:
                value = self.deg2rad(value)
            yield value
