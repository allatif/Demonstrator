import math as m

import pygame as pg
import pygame.gfxdraw

from .. import pg_init, pg_root, setup_sim

from .. components import color, gaussian
from .. interface import slider


class PoleMap(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.plane = gaussian.Plane(self.width, self.height)
        self.next = "EULER"
        self.sim = setup_sim.SimData(12000)
        self.poles = None
        # self.controller = [-2196.6, -4761.2, -51800, -18831]
        # self.controller = [-1296.6, -3161.2, -31800, -9831]
        # self.controller = [-1196.6, -3761.2, -11800, -8831]
        # for testing fall of sphere
        self.controller = [-9050, -3150, -4800, -9750]
        self.sliders = []

        slider_ranges = [(0, 10000), (0, 10000), (0, 80000), (0, 50000)]

        for slider_range, c in zip(slider_ranges, self.controller):
            self.sliders.append(slider.Slider(-c, 20, 20, 200, slider_range))

        for slider_ in self.sliders:
            slider_.thumb.c_x = slider_.get_thumb_from_value()

        font_size = self.sliders[0].value_label.size
        self.font = pg.font.SysFont('Liberation Sans', font_size)
        self.hudfont = pg.font.SysFont('Consolas', 12)

        self.options = {"Hud position": 'left'}
        self.loop_counter = 0

    def cleanup(self):
        self.done = False
        self.persist["controller"] = self.controller
        return self.persist

    def get_event(self, event, mouse):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
            if event.key == pg.K_F1:
                self.options["Hud position"] = 'left'
            if event.key == pg.K_F2:
                self.options["Hud position"] = 'right'

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            print(self.plane.get_point(mouse))

            for slider_ in self.sliders:
                if slider_.thumb.mouse_inside(mouse):
                    slider_.thumb.grab()
                    break

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for slider_ in self.sliders:
                if slider_.thumb.grabbed:
                    slider_.thumb.release()
                    break

    def update(self, surface, mouse):
        self.poles = []
        self.controller = []

        for slider_ in self.sliders:
            if slider_.thumb.grabbed:
                slider_.slide(mouse)
            slider_.update()
            self.controller.append(-slider_.value)

        self.sim.set_regs(*self.controller)
        self.sim.update()

        for pole in self.sim.get_poles():
            pos = self.plane.get_pos_from_point((pole.real, pole.imag))
            self.poles.append(gaussian.Pole(pos, 15, pole.real, pole.imag))

        self.draw(surface)

    def draw(self, surface):
        surface.fill(color.WHITE)
        self.draw_coordlines(surface, self.plane.Re_axis, self.plane.Im_axis)
        self.draw_axes(surface, self.plane.Re_axis, self.plane.Im_axis)
        self.draw_hud(surface, 115, 66, pos=self.options["Hud position"])

        for pole in self.poles:
            pos = pole.get_center()
            dyn_color = color.LBLUE
            if pole.is_unstable():
                dyn_color = color.RED
                # animate unstable pole flicker
                signal = self.gen_signal_by_loop(4, 80)
                self._draw_aafilled_circle(surface, *pos,
                                           pole.r + round(signal),
                                           color.ARED)
            elif pole.is_marginal_stable():
                dyn_color = color.ORANGE
            self._draw_aafilled_circle(surface, *pos, pole.r, dyn_color)

        self.draw_interface(surface)

    def draw_axes(self, surface, axis_1, axis_2):
        d = {0: axis_1, 1: axis_2}
        for axis in range(2):
            pg.draw.line(surface, color.BLACK,
                         *d[axis].get_line(), d[axis].thickness)

    def draw_coordlines(self, surface, axis_1, axis_2, grid=True):
        d = {0: axis_1, 1: axis_2}
        linecolor = color.LGREY
        thickness = 1
        if not grid:
            linecolor = color.BLACK
            thickness = 2

        for axis in range(2):
            lines = d[axis].get_coordlines(grid)
            for line in lines:
                pg.draw.line(surface, linecolor, *line, thickness)

    def draw_interface(self, surface):
        for slider_ in self.sliders:
            pg.gfxdraw.box(surface, slider_.track.rect, color.GREY)
            pg.gfxdraw.box(surface, slider_.get_slid_rect(), color.ORANGE)

            self._draw_aafilled_circle(surface, slider_.thumb.c_x,
                                       slider_.thumb.c_y,
                                       slider_.thumb.r,
                                       color.TOMATO)

            text = self.font.render(str(slider_.value), True, color.ORANGE)
            surface.blit(text, slider_.value_label.rect)

    def draw_hud(self, surface, length, wide, margin=4, pos='right'):
        rect = (self.width//2, self.height//2, length, wide)
        text_margin = 5
        line_margin = 14

        for num, pole in enumerate(self.poles):
            pole_str = f'{pole}'
            text = self.hudfont.render(pole_str, True, color.WHITE)
            if pole.is_unstable():
                text = self.hudfont.render(pole_str, True, color.LRED)

            if pos == 'left':
                hud_pos_x = margin
                hud_pos_y = self.height - margin - wide
                rect = (hud_pos_x, hud_pos_y, length, wide)
                if num == 0:
                    pg.gfxdraw.box(surface, rect, (0, 0, 0, 200))
                surface.blit(text,
                             (hud_pos_x + text_margin,
                              hud_pos_y + text_margin + num*line_margin))
            elif pos == 'right':
                hud_pos_x = self.width - margin - length
                hud_pos_y = self.height - margin - wide
                rect = (hud_pos_x, hud_pos_y, length, wide)
                if num == 0:
                    pg.gfxdraw.box(surface, rect, (0, 0, 0, 200))
                surface.blit(text,
                             (hud_pos_x + text_margin,
                              hud_pos_y + text_margin + num*line_margin))

    def gen_signal_by_loop(self, amplitude, length):
        self.loop_counter += 1
        return amplitude * m.sin((self.loop_counter/length) * m.pi)**2

    @staticmethod
    def _draw_aafilled_circle(surface, x, y, r, color):
        pg.gfxdraw.aacircle(surface, x, y, r, color)
        pg.gfxdraw.filled_circle(surface, x, y, r, color)
