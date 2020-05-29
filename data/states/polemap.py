import math as m

import pygame as pg
import pygame.gfxdraw
import matplotlib.pyplot as plt

from .. import pg_init, pg_root, setup_sim

from .. components import colors, tools, gaussian
from .. interface import slider, button, checkbox


class PoleMap(pg_root._State):

    def __init__(self, mother=True):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.plane = gaussian.Plane(self.width, self.height)

        self.sim_ref_state = (0.5, 0)
        self.sim_init_state = (0, 0, 0, 0.3)
        self.limitations = (0.56, 0.56)
        self.model = setup_sim.StateSpaceModel()
        self.poles = None
        self.results = None

        self.Kregs = [-1296.6, -3161.2, -31800, -9831]

        # Initialize sliders
        self.sliders = []
        slider_ranges = [(0, -10000), (0, -20000), (0, -180000), (0, -60000)]
        for r in slider_ranges:
            self.sliders.append(slider.Slider(r, 2, 200, colors.CORAL_PACK))
        # # Group up sliders
        self.sliders[-1].group((20, 20), header_text='Controller Settings',
                               header_size=16)
        # # Set sliders according to Kreg
        for slider_, value in zip(self.sliders, self.Kregs):
            slider_.set(value)

        # Initialize checkbox
        # # Checkbox position depends on last slider
        cb_pos_x = self.sliders[len(self.sliders)-1].pos[0]
        cb_pos_y = self.sliders[len(self.sliders)-1].pos[1] + 20
        self.checkbox = checkbox.CheckBox(16, 2, colors.BLACK)
        self.checkbox.set_pos(cb_pos_x, cb_pos_y)
        self.checkbox.set_label('Switch off Controller', margin=5)

        # Initialize buttons
        self.but_set = button.Button(text='Settings', bg=colors.LBLUE,
                                     fg=colors.WHITE, action='SETTINGS')
        self.but_set.set_pos(self.width-self.but_set.width-15, 10)

        self.but_plot = button.Button(text='Show Plot', bg=colors.LRED,
                                      fg=colors.WHITE, action=self._plot)
        self.but_plot.set_pos(self.but_set.pos[0]-self.but_plot.width-15, 10)
        self.but_plot.activate_reflection()

        self.options = {"Hud position": 'left'}

        self.polemap_imagestr = ''

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)

        self.next = "GAME"
        if self.previous == 'GAME':
            self.but_plot.virgin = True

        if self.previous is not 'SPLASH':
            self.sim_ref_state = self.persist["sim reference state"]
            self.sim_init_state = self.persist["sim initial state"]
            self.limitations = self.persist["limitations"]

        if "result" in self.persist:
            self.results = self.persist["result"]

    def cleanup(self):
        self.done = False
        self.persist["sim reference state"] = self.sim_ref_state
        self.persist["sim initial state"] = self.sim_init_state
        self.persist["limitations"] = self.limitations
        self.persist["controller"] = self.Kregs
        self.persist["mode"] = 'ss_controller'

        if self.checkbox.checked:
            self.persist["mode"] = 'user'

        self.persist["bg_image"] = self.screenshot

        if self.next == 'SPLASH':
            if "result" in self.persist:
                del self.persist["result"]
                self.results = None

        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
            if event.key == pg.K_BACKSPACE:
                self.next = "SPLASH"
                self.done = True
            if event.key == pg.K_F1:
                self.options["Hud position"] = 'left'
            if event.key == pg.K_F2:
                self.options["Hud position"] = 'right'
            if event.key == pg.K_KP_PLUS:
                self.plane.Re_axis.zoom()
                self.plane.Im_axis.zoom()
            if event.key == pg.K_KP_MINUS:
                self.plane.Re_axis.zoom(dir='out')
                self.plane.Im_axis.zoom(dir='out')

    def update(self, surface):
        if self.checkbox.checked:
            self.Kregs = [0, 0, 0, 0]
            for sldr in self.sliders:
                sldr.active = False
        else:
            for sldr in self.sliders:
                sldr.active = True
            self.Kregs = slider.Slider.groups[1].get_values()

        self.model.set_Kregs(*self.Kregs)
        self.model.update()

        self.poles = []
        for pole in self.model.get_poles():
            pos = self.plane.get_pos_from_point((pole.real, pole.imag))
            self.poles.append(gaussian.Pole(pos, 15, pole.real, pole.imag))

        if self.but_set.pressed:
            self.save_screen(surface)

        self.draw(surface)

    def draw(self, surface):
        surface.fill(colors.WHITE)
        self.draw_coordlines(surface, self.plane.Re_axis, self.plane.Im_axis)
        self.draw_axes(surface, self.plane.Re_axis, self.plane.Im_axis)

        # Animate unstable pole flicker via signal
        signal_length = self.static_fps // 2
        signal = self.gen_signal_by_loop(4, signal_length, for_obj='Pole')
        for pole in self.poles:
            pos = pole.get_center()
            Re_scale = self.plane.Re_axis.get_scale()
            Im_scale = self.plane.Im_axis.get_scale()
            if Re_scale <= 12 or Im_scale <= 12:
                pole.shrink()
            else:
                pole.norm()

            dyn_color = colors.LBLUE
            if pole.is_unstable():
                dyn_color = colors.RED
                # Draw flicker light circle (transparent red)
                tools.draw_aafilled_circle(surface, *pos,
                                           pole.r + round(signal),
                                           colors.ARED)
            elif pole.is_marginal_stable():
                dyn_color = colors.CORAL

            tools.draw_aafilled_circle(surface, *pos, pole.r, dyn_color)

        self.draw_interface(surface)
        self.draw_hud(surface, 115, 66, pos=self.options["Hud position"])

    def draw_axes(self, surface, axis_1, axis_2):
        d = {0: axis_1, 1: axis_2}
        for axis in range(2):
            pg.draw.line(surface, colors.BLACK,
                         *d[axis].get_line(), d[axis].thickness)

    def draw_coordlines(self, surface, axis_1, axis_2, grid=True):
        d = {0: axis_1, 1: axis_2}
        linecolor = colors.LGREY
        thickness = 1
        if not grid:
            linecolor = colors.BLACK
            thickness = 2

        for axis in range(2):
            lines = d[axis].get_coordlines(grid)
            for line in lines:
                pg.draw.line(surface, linecolor, *line, thickness)

    def draw_interface(self, surface):
        slider.Slider.groups[1].draw(surface)
        self.checkbox.draw(surface)
        self.but_set.draw(surface)

        if self.results is not None:
            self.but_plot.draw(surface)

    def draw_hud(self, surface, width, height, margin=4, pos='left'):
        text_margin = 5
        line_margin = 14

        rect = self.render_hud(width, height, margin, pos)
        hudcolor = colors.TRAN200

        pg.gfxdraw.box(surface, rect, hudcolor)

        for num, pole in enumerate(self.poles):
            pole_str = f'{pole}'
            text_color = colors.LRED if pole.is_unstable() else colors.WHITE
            text = self.hudfont.render(pole_str, True, text_color)

            surface.blit(text, (rect[0] + text_margin,
                                rect[1] + text_margin + num*line_margin))

    def gen_signal_by_loop(self, amplitude, length, for_obj='Pole'):
        """Generates sinus signal from loop counter where argument length
        controls the frequency of flickering. Should vary when fps changed."""

        self.run_loop_counter()
        if for_obj == 'Pole':
            return amplitude * m.sin((self._i_/length) * m.pi)**2

    def _plot(self):
        if self.results is not None:
            x, ang, time = self.results
            plt.figure(figsize=(12, 8), dpi=80,
                       facecolor=(colors.get_pp(colors.WHITE)))

            plt.subplot(211)
            plt.plot(time, x, color=colors.get_pp(colors.LBLUE))
            plt.xlabel('Time [s]')
            plt.ylabel('Velocity [m/s]')
            plt.grid(True)

            plt.subplot(212)
            plt.plot(time, ang, color=colors.get_pp(colors.TOMATO))
            plt.xlabel('Time [s]')
            plt.ylabel('Angle [°]')
            plt.grid(True)

            plt.show()
