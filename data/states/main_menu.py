import math as m

import pygame as pg
import pygame.gfxdraw


from .. import pg_init, pg_root

from .. components import colors
from .. interface import window, slider_group, slider
from .. interface import button, checkbox_group, checkbox


class MainSetup(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.next = "SPLASH"
        self.predone = False

        self.win = window.MenuWindow('Main Settings')
        self.win.cache_font(self.win.header, 'Liberation Sans', 32,
                            colors.WHITE)

        # Initialize button
        self.but_ok = button.Button('OK', colors.RED_PACK, colors.WHITE)
        self.but_ok.set_pos(self.win.con_right-self.but_ok.width,
                            self.win.con_bottom-self.but_ok.height)

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.game_fps_bins = self.persist["game fps binaries"]
        self.euler_ministeps = self.persist["euler ministeps"]

        self._init_fps_checkboxes()
        self.cbox_group = checkbox_group \
            .CheckboxGroup(self.fps_cboxes, header_text='In game frame rate',
                           header_size=26)
        self.cbox_group.arrange(self.win.con_pos[0]+10,
                                self.win.con_pos[1]+75)

        self._init_euler_setup_sliders()
        self.slider_group = slider_group \
            .SliderGroup(self.euler_sliders,
                         header_text='Euler steps per frame', header_size=26)
        self.slider_group.arrange(self.win.con_pos[0]+10,
                                  self.win.con_pos[1]+225)

        self.bg_img = pg.image.fromstring(self.persist["bg_image"],
                                          (self.width, self.height), 'RGB')

    def cleanup(self):
        self.done = False
        self.predone = False
        self.persist["game fps binaries"] = self.game_fps_bins
        self.persist["euler ministeps"] = self.euler_ministeps
        return self.persist

    def _init_fps_checkboxes(self):
        # Initialize checkboxes for choosing fps
        self.fps_cboxes = []
        cbox_labels = ['60 fps', '100 fps']
        zipped = zip(cbox_labels, self.game_fps_bins)
        for cbox_label, bool_ in zipped:
            self.fps_cboxes.append(checkbox.CheckBox(24, 3, colors.WHITE,
                                                     bool_, name=cbox_label,
                                                     type_='radio'))

    def _init_euler_setup_sliders(self):
        # Initialize sliders for Euler mini steps setup
        self.euler_sliders = []
        ranges = [(1, 100)]
        units = ['step(s)']
        self.euler_sliders.append(
            slider.Slider(self.euler_ministeps, ranges[0], 4, 250,
                          colors.GREEN_PACK, name=None, margin=15,
                          unit=units[0]))
        self.euler_sliders[0].settings['integer'] = True

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for num, cbox in enumerate(self.fps_cboxes):
                if cbox.mouseover:
                    self.cbox_group.select_checkbox(num)
                    break

            for sldr in self.euler_sliders:
                if sldr.thumb.mouseover:
                    sldr.thumb.grab()
                    break

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for sldr in self.euler_sliders:
                if sldr.thumb.grabbed:
                    sldr.thumb.release()
                    break

            if self.but_ok.mouseover:
                self.predone = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            for sldr in self.euler_sliders:
                if sldr.thumb.mouseover:
                    pass

    def mouse_logic(self, mouse):
        for cbox in self.fps_cboxes:
            self.hover_object_logic(mouse, cbox)
        for sldr in self.euler_sliders:
            self.instrument_logic(mouse, sldr)
        self.hover_object_logic(mouse, self.but_ok)

    def update(self, surface):
        self.cbox_group.update()
        self.draw(surface)

        # When press OK-button
        # Before state is going to close it will save the new initial cond.
        if self.predone:
            self.game_fps_bins = self.cbox_group.get_bools()
            self.euler_ministeps = self.slider_group.get_values()[0]
            self.done = True

    def draw(self, surface):
        surface.blit(self.bg_img, pg_init.SCREEN_RECT)
        pg.gfxdraw.box(surface, self.win.rect, colors.TRAN225)

        self.draw_heading(surface)
        self.draw_checkbox_group(surface, self.cbox_group)
        self.draw_slider_group(surface, self.slider_group)
        self.draw_button(surface, self.but_ok)

    def draw_heading(self, surface):
        surface.blit(self.win.font_cache, self.win.con_pos)

    def _state_in_rad(self, state):
        for num, value in enumerate(state):
            if num > len(state)//2-1:
                value = m.radians(value)
            yield value
