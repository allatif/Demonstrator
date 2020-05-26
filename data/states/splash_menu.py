import math as m

import pygame as pg
import pygame.gfxdraw


from .. import pg_init, pg_root

from .. components import colors
from .. interface import window, slider, button, checkbox


class MainSetup(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.next = "SPLASH"

        # Initialize menu window
        self.win = window.MenuWindow('Main Settings')
        self.win.cache_font(self.win.header, 'Liberation Sans', 32,
                            colors.WHITE)

        # Initialize button
        self.but_ok = button.Button(text='OK', bg=colors.LRED, fg=colors.WHITE,
                                    action=self._save_settings, done=True)
        self.but_ok.set_pos(self.win.con_right-self.but_ok.width,
                            self.win.con_bottom-self.but_ok.height)

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.game_fps_bins = self.persist["game fps binaries"]
        self.euler_ministeps = self.persist["euler ministeps"]

        # Initialize checkboxes for choosing fps
        self.fps_cboxes = []
        cbox_labels = ['60 fps', '100 fps']
        zipped = zip(cbox_labels, self.game_fps_bins)
        for cbox_label, bool_ in zipped:
            self.fps_cboxes.append(checkbox.CheckBox(24, 3, colors.WHITE,
                                                     bool_, name=cbox_label,
                                                     type_='radio'))
        self.fps_cboxes[-1].group(
            (self.win.con_pos[0]+10, self.win.con_pos[1]+75),
            header_text='In game frame rate', header_size=26
        )

        # Initialize slider for Euler mini steps setup
        range_ = (1, 100)
        unit = 'step(s)'
        self.slider = slider.Slider(range_, 4, 250, colors.GREEN_PACK,
                                    margin=15, unit=unit, default=10)
        self.slider.settings['integer'] = True
        self.slider.group((self.win.con_pos[0]+10, self.win.con_pos[1]+225),
                          header_text='Euler steps per frame', header_size=26)
        self.slider.set(self.euler_ministeps)

        self.bg_img = self.persist["bg_image"]

    def cleanup(self):
        self.done = False
        self.persist["game fps binaries"] = self.game_fps_bins
        self.persist["euler ministeps"] = self.euler_ministeps
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True

    def update(self, surface):
        self.draw(surface)

    def draw(self, surface):
        surface.blit(self.bg_img, pg_init.SCREEN_RECT)
        pg.gfxdraw.box(surface, self.win.rect, colors.TRAN225)

        self.draw_heading(surface)
        self.draw_checkbox_group(surface, checkbox.CheckBox.groups[1])
        self.draw_instrument_group(surface, slider.Slider.groups[1])
        self.draw_button(surface, self.but_ok)

    def draw_heading(self, surface):
        surface.blit(self.win.font_cache, self.win.con_pos)

    def _save_settings(self):
        self.game_fps_bins = checkbox.CheckBox.groups[1].get_bools()
        self.euler_ministeps = slider.Slider.groups[1].get_values()[0]

    def _state_in_rad(self, state):
        for num, value in enumerate(state):
            if num > len(state)//2-1:
                value = m.radians(value)
            yield value
