import math as m

import pygame as pg
import pygame.gfxdraw
import matplotlib.pyplot as plt

from .. import pg_init, pg_root, setup_sim

from .. components import color, gaussian
from .. interface import slider, button


class PoleMap(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.plane = gaussian.Plane(self.width, self.height)
        self.next = "EULER"
        self.sim = setup_sim.SimData(12000)
        self.poles = None
        self.results = None
        # self.controller = [-2196.6, -4761.2, -51800, -18831]
        self.controller = [-1296.6, -3161.2, -31800, -9831]
        # self.controller = [-1196.6, -3761.2, -11800, -8831]
        # for testing fall of sphere
        # self.controller = [-9050, -3150, -4800, -9750]
        self.sliders = []

        slider_ranges = [(0, 10000), (0, 10000), (0, 80000), (0, 50000)]

        for slider_range, c in zip(slider_ranges, self.controller):
            self.sliders.append(slider.Slider(-c, 20, 20, 200, slider_range))

        for slider_ in self.sliders:
            slider_.thumb.c_x = slider_.get_thumb_from_value()

        self.button = button.Button((90, 30), 'Show Plot', color.LRED)
        self.button.set_pos((self.width-self.button.width-15, 10))
        self.button.init_reflection()

        font_size = self.sliders[0].value_label.size
        self.font = pg.font.SysFont('Liberation Sans', font_size)
        self.smallfont = pg.font.SysFont('Liberation Sans', 14)
        self.hudfont = pg.font.SysFont('Consolas', 12)

        self.options = {"Hud position": 'left', "Euler corr": True}
        self.loop_counter = 0

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.results = self.persist["result"]

    def cleanup(self):
        self.done = False
        self.button.virgin = True
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
            if event.key == pg.K_c:
                self.options["Euler corr"] = not self.options["Euler corr"]

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

            if self.button.inside(mouse):
                self.plot()

        if self.button.inside(mouse):
            self.button.color = color.LLRED
            self.button.virgin = False
        else:
            self.button.color = self.button.orgcolor

    def update(self, surface, mouse):
        self.poles = []
        self.controller = []

        # Euler method causes a little error per step k
        # Need of correction offset 'crr' to correct marginal stable poles
        crr = 0.0485 if self.options['Euler corr'] else 0.0

        for slider_ in self.sliders:
            if slider_.thumb.grabbed:
                slider_.slide(mouse)
            slider_.update()
            self.controller.append(-slider_.value)

        self.sim.set_regs(*self.controller)
        self.sim.update()

        for pole in self.sim.get_poles():
            pos = self.plane.get_pos_from_point((pole.real+crr, pole.imag))
            self.poles.append(gaussian.Pole(pos, 15, pole.real+crr, pole.imag))

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
                signal = self.gen_signal_by_loop(4, 80, forobj='Pole')
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
        last_slider_rect = None
        for slider_ in self.sliders:
            pg.gfxdraw.box(surface, slider_.track.rect, color.GREY)
            pg.gfxdraw.box(surface, slider_.get_slid_rect(), color.ORANGE)

            self._draw_aafilled_circle(surface, slider_.thumb.c_x,
                                       slider_.thumb.c_y,
                                       slider_.thumb.r,
                                       color.TOMATO)

            text = self.font.render(str(slider_.value), True, color.ORANGE)
            surface.blit(text, slider_.value_label.rect)
            last_slider_rect = slider_.track.rect

        if self.options["Euler corr"]:
            # Show if option Euler method correction offset is activated
            msg = '*Imaginary axis offset'
            text = self.smallfont.render(msg, True, color.DBLUE)
            left, top, w, h = last_slider_rect
            surface.blit(text, (left, top+15, w, h))

        if self.results is not None:
            # Show Plot Button
            pg.gfxdraw.box(surface, self.button.rect, self.button.color)

            # Button Reflection
            if self.button.virgin:
                signal = self.gen_signal_by_loop(4, 80, forobj='But_Refl')
                self.button.run(signal)
                self._draw_aafilled_polygon(surface,
                                            self.button.get_refl_poly(),
                                            color.LLRED)

            # Button Text
            text, rect = self.render_font(self.button.text, 'Liberation Sans',
                                          16, color.WHITE, self.button.center)
            surface.blit(text, rect)

    def draw_hud(self, surface, length, wide, margin=4, pos='right'):
        text_margin = 5
        line_margin = 14

        rect = self.render_hud(length, wide, margin, pos)
        hudcolor = color.A200DDBLUE if self.options['Euler corr'] \
            else color.TRAN200
        pg.gfxdraw.box(surface, rect, hudcolor)

        for num, pole in enumerate(self.poles):
            pole_str = f'{pole}'
            textcolor = color.LRED if pole.is_unstable() else color.WHITE
            text = self.hudfont.render(pole_str, True, textcolor)

            surface.blit(text, (rect[0] + text_margin,
                                rect[1] + text_margin + num*line_margin))

    def plot(self):
        if self.results is not None:
            x, ang, time = self.results
            plt.figure(figsize=(12, 8), dpi=80,
                       facecolor=(color.get_pp(color.WHITE)))

            plt.subplot(211)
            plt.plot(time, x, color=color.get_pp(color.LBLUE))
            plt.xlabel('Time [s]')
            plt.ylabel('Distance [m]')
            plt.grid(True)

            plt.subplot(212)
            plt.plot(time, ang, color=color.get_pp(color.TOMATO))
            plt.xlabel('Time [s]')
            plt.ylabel('Angle [°]')
            plt.grid(True)

            plt.show()

    def gen_signal_by_loop(self, amplitude, length, forobj='Pole'):
        self.loop_counter += 1
        if forobj == 'Pole':
            return amplitude * m.sin((self.loop_counter/length) * m.pi)**2
        elif forobj == 'But_Refl':
            return not (self.loop_counter % 1)

    @staticmethod
    def _draw_aafilled_circle(surface, x, y, r, color):
        pg.gfxdraw.aacircle(surface, x, y, r, color)
        pg.gfxdraw.filled_circle(surface, x, y, r, color)

    @staticmethod
    def _draw_aafilled_polygon(surface, points, color):
        pg.gfxdraw.aapolygon(surface, points, color)
        pg.gfxdraw.filled_polygon(surface, points, color)
