import math as m

import pygame as pg
import pygame.gfxdraw


from .. import pg_init, pg_root

from .. components import colors
from .. interface import window, slider_group, slider, button, knob


class SetupMenu(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.predone = False

        self.win = window.MenuWindow('Settings Menu')
        self.win.cache_font(self.win.header, 'Liberation Sans', 32,
                            colors.WHITE)

        # Initialize button
        self.but_ok = button.Button('OK', colors.RED_PACK, colors.WHITE)
        self.but_ok.set_pos(self.win.con_right-self.but_ok.width,
                            self.win.con_bottom-self.but_ok.height)

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.next = self.previous
        self.sim_ref_state = self.persist["sim reference state"]
        self.sim_init_state = self.persist["sim initial state"]

        self._init_cond_sliders()
        self.slider_group_a = slider_group \
            .SliderGroup(self.cond_sliders, header_text='Initial Conditions',
                         header_size=26)
        self.slider_group_a.arrange(self.win.con_pos[0]+10,
                                    self.win.con_pos[1]+75)

        self._init_ref_instruments()
        self.slider_group_b = slider_group \
            .SliderGroup(self.ref_instrs, header_text='Reference State',
                         header_size=26)
        self.slider_group_b.arrange(self.win.con_pos[0]+435,
                                    self.win.con_pos[1]+75)

        self.bg_img = pg.image.fromstring(self.persist["bg_image"],
                                          (self.width, self.height), 'RGB')

    def cleanup(self):
        self.done = False
        self.predone = False
        self.persist["sim reference state"] = self.sim_ref_state
        self.persist["sim initial state"] = self.sim_init_state
        return self.persist

    def _init_cond_sliders(self):
        # Initialize sliders for initial conditions
        self.cond_sliders = []
        slider_ranges = [(-2, 2), (-2, 2), (-10, 10), (-20, 20)]
        zipped = zip(slider_ranges, self.sim_init_state)
        slider_names = ['x', 'v', 'φ', 'ω']
        units = ['m', 'm/s', '°', '°/s']
        for num, (slider_range, val) in enumerate(zipped):
            if num > 1:
                val = m.degrees(val)
            self.cond_sliders.append(slider.Slider(val, slider_range, 4, 250,
                                                   colors.GREEN_PACK,
                                                   name=slider_names[num],
                                                   margin=15, unit=units[num]))

    def _init_ref_instruments(self):
        # Initialize sliders and control knob for reference state
        self.ref_instrs = []
        vel, ang = self.sim_ref_state
        ranges = [(-2, 2), (9.9, -9.9)]
        names = ['x', 'φ']
        units = ['m', '°']
        self.ref_instrs.append(
            slider.Slider(vel, ranges[0], 4, 250, colors.ORANGE_PACK,
                          name=names[0], margin=15, unit=units[0]))

        self.ref_instrs.append(
            knob.ControlKnob(m.degrees(ang), ranges[1], 51, 32,
                             colors.ORANGE_PACK, name=names[1], margin=24,
                             unit=units[1]))

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for instr in self.cond_sliders+self.ref_instrs:
                if instr.thumb.mouseover:
                    instr.thumb.grab()
                    break

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for instr in self.cond_sliders+self.ref_instrs:
                if instr.thumb.grabbed:
                    instr.thumb.release()
                    break

            if self.but_ok.mouseover:
                self.predone = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            for instr in self.cond_sliders+self.ref_instrs:
                if instr.thumb.mouseover:
                    instr.zeroize()

    def mouse_logic(self, mouse):
        for instr in self.cond_sliders+self.ref_instrs:
            self.instrument_logic(mouse, instr)
        self.hover_object_logic(mouse, self.but_ok)

    def update(self, surface):
        self.draw(surface)

        # When press OK-button
        # Before state is going to close it will save the new initial cond.
        if self.predone:
            init_state = self.slider_group_a.get_values()
            ref_state = self.slider_group_b.get_values()
            self.sim_init_state = list(self._state_in_rad(init_state))
            self.sim_ref_state = list(self._state_in_rad(ref_state))
            self.done = True

    def draw(self, surface):
        surface.blit(self.bg_img, pg_init.SCREEN_RECT)
        pg.gfxdraw.box(surface, self.win.rect, colors.TRAN225)

        self.draw_heading(surface)
        self.draw_slider_group(surface, self.slider_group_a)
        self.draw_slider_group(surface, self.slider_group_b)
        self.draw_button(surface, self.but_ok)

    def draw_heading(self, surface):
        surface.blit(self.win.font_cache, self.win.con_pos)

    def _state_in_rad(self, state):
        for num, value in enumerate(state):
            if num > len(state)//2-1:
                value = m.radians(value)
            yield value
