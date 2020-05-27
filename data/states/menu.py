import math as m

import pygame as pg
import pygame.gfxdraw


from .. import pg_init, pg_root

from .. components import colors
from .. interface import window, slider, knob, button


class SetupMenu(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.next = "POLEMAP"

        # Initialize menu window
        self.win = window.MenuWindow('Settings Menu')
        self.win.cache_font(self.win.header, 'Liberation Sans', 32,
                            colors.WHITE)

        # Initialize button
        self.but_ok = button.Button(text='OK', bg=colors.LRED, fg=colors.WHITE,
                                    action=self._save_settings, done=True)
        self.but_ok.set_pos(self.win.con_right-self.but_ok.width,
                            self.win.con_bottom-self.but_ok.height)

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.next = self.previous
        self.sim_ref_state = self.persist["sim reference state"]
        self.sim_init_state = self.persist["sim initial state"]
        self.limitations = self.persist["limitations"]

        self._init_cond_sliders()
        self._init_ref_instruments()
        self._init_lim_sliders()

        self.bg_img = self.persist["bg_image"]

    def cleanup(self):
        self.done = False
        self.persist["sim reference state"] = self.sim_ref_state
        self.persist["sim initial state"] = self.sim_init_state
        self.persist["limitations"] = self.limitations
        return self.persist

    def _init_cond_sliders(self):
        # Initialize sliders for initial conditions
        self.cond_sliders = []
        slider_ranges = [(-2, 2), (-2, 2), (-10, 10), (-20, 20)]
        slider_names = ['x', 'v', 'φ', 'ω']
        units = ['m', 'm/s', '°', '°/s']
        for r, n, u in zip(slider_ranges, slider_names, units):
            self.cond_sliders.append(slider.Slider(r, 4, 250, colors.GREEN_PACK,
                                                   name=n, margin=15, unit=u))
        # # Group up sliders
        pos = (self.win.con_pos[0]+10, self.win.con_pos[1]+75)
        self.cond_sliders[-1].group(pos, header_text='Initial Conditions',
                                    header_size=26)
        # # Set sliders according to sim_init_state
        zipped = zip(self.cond_sliders, self.sim_init_state)
        for num, (slider_, value) in enumerate(zipped):
            if num > 1:
                value = m.degrees(value)
            slider_.set(value)

    def _init_ref_instruments(self):
        # Initialize sliders and control knob for reference state
        ranges = [(-2, 2), (9.9, -9.9)]
        names = ['x', 'φ']
        units = ['m', '°']
        self.ref_slider = slider.Slider(ranges[0], 4, 250, colors.ORANGE_PACK,
                                        name=names[0], margin=15, unit=units[0])

        self.ref_knob = knob.ControlKnob(ranges[1], 51, 32, colors.ORANGE_PACK,
                                         name=names[1], margin=24,
                                         unit=units[1])
        # # Group up instruments
        pos = (self.win.con_pos[0]+435, self.win.con_pos[1]+75)
        self.ref_knob.group(pos, header_text='Reference State', header_size=26)
        # # Set instruments according to sim_ref_state
        vel, ang = self.sim_ref_state
        self.ref_slider.set(vel)
        self.ref_knob.set(m.degrees(ang))

    def _init_lim_sliders(self):
        # Initialize sliders for location limitions
        self.lim_sliders = []
        slider_ranges = [(0, 1.56), (0, 1.56)]
        slider_names = ['L', 'R']
        units = ['m', 'm']
        for r, n, u in zip(slider_ranges, slider_names, units):
            self.lim_sliders.append(slider.Slider(r, 4, 250, colors.RED_PACK,
                                                  name=n, margin=15, unit=u,
                                                  default=0.56))
        # # Group up sliders
        pos = (self.win.con_pos[0]+10, self.win.con_pos[1]+285)
        self.lim_sliders[-1].group(pos, header_text='Limitations',
                                   header_size=26)
        # # Set sliders according to sim_init_state
        zipped = zip(self.lim_sliders, self.limitations)
        for slider_, value in zipped:
            slider_.settings["decimal places"] = 2
            slider_.set(value)

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
        self.draw_interface(surface)

    def draw_interface(self, surface):
        slider.Slider.groups[1].draw(surface)
        slider.Slider.groups[2].draw(surface)
        slider.Slider.groups[3].draw(surface)
        self.but_ok.draw(surface)

    def draw_heading(self, surface):
        surface.blit(self.win.font_cache, self.win.con_pos)

    def _save_settings(self):
        init_state = slider.Slider.groups[1].get_values()
        ref_state = slider.Slider.groups[2].get_values()
        limits = slider.Slider.groups[3].get_values()
        self.sim_init_state = list(self._state_in_rad(init_state))
        self.sim_ref_state = list(self._state_in_rad(ref_state))
        self.limitations = list(limits)

    def _state_in_rad(self, state):
        for num, value in enumerate(state):
            if num > len(state)//2-1:
                value = m.radians(value)
            yield value
