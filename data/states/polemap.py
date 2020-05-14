import math as m

import pygame as pg
import pygame.gfxdraw
import matplotlib.pyplot as plt

from .. import pg_init, pg_root, setup_sim

from .. components import colors, gaussian
from .. interface import slider_group, slider, button, checkbox


class PoleMap(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.plane = gaussian.Plane(self.width, self.height)
        self.next = "GAME"
        self.sim_ref_state = (0.5, 0)
        self.sim_init_state = (0, 0, 0, 0.3)
        self.model = setup_sim.StateSpaceModel()
        self.poles = None
        self.results = None

        self.Kregs = [-1296.6, -3161.2, -31800, -9831]

        # Initialize sliders
        self.sliders = []
        slider_ranges = [(0, -10000), (0, -20000), (0, -180000), (0, -60000)]
        for slider_range, val in zip(slider_ranges, self.Kregs):
            self.sliders.append(slider.Slider(val, slider_range, 2, 200,
                                              colors.CORAL_PACK))
        self.slider_group = slider_group \
            .SliderGroup(self.sliders, header_text='Controller Settings',
                         header_size=16)
        self.slider_group.arrange(20, 20)

        # Initialize checkbox
        # # Checkbox position depends on last slider
        cb_pos_x = self.sliders[len(self.sliders)-1].pos[0]
        cb_pos_y = self.sliders[len(self.sliders)-1].pos[1] + 20
        self.checkbox = checkbox.CheckBox(16, 2, colors.BLACK)
        self.checkbox.set_pos(cb_pos_x, cb_pos_y)
        self.checkbox.set_label('Switch off Controller', margin=5)

        # Initialize buttons
        self.but_set = button.Button('Settings', colors.BLUE_PACK, colors.WHITE)
        self.but_set.set_pos(self.width-self.but_set.width-15, 10)

        self.but_plot = button.Button('Show Plot', colors.RED_PACK,
                                      colors.WHITE)
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

        if "result" in self.persist:
            self.results = self.persist["result"]

    def cleanup(self):
        self.done = False
        self.persist["sim reference state"] = self.sim_ref_state
        self.persist["sim initial state"] = self.sim_init_state
        self.persist["controller"] = self.Kregs
        self.persist["mode"] = 'ss_controller'
        if self.checkbox.checked:
            self.persist["mode"] = 'user'
        self.persist["bg_image"] = self.screenshot_imagestr
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

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.checkbox.mouseover:
                self.checkbox.checked = not self.checkbox.checked

            if not self.checkbox.checked:
                for sldr in self.sliders:
                    if sldr.thumb.mouseover:
                        sldr.thumb.grab()
                        break

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if not self.checkbox.checked:
                for sldr in self.sliders:
                    if sldr.thumb.grabbed:
                        sldr.thumb.release()
                        break

            if self.but_set.mouseover:
                self.next = "SETTINGS"
                self.done = True

            if self.but_plot.mouseover:
                self.plot()

    def mouse_logic(self, mouse):
        for instr in self.sliders:
            self.instrument_logic(mouse, instr)
        self.hover_object_logic(mouse, self.checkbox)
        self.hover_object_logic(mouse, self.but_set)
        self.hover_object_logic(mouse, self.but_plot)

    def update(self, surface):
        if self.checkbox.checked:
            self.Kregs = [0, 0, 0, 0]
            for sldr in self.sliders:
                sldr.active = False
        else:
            for sldr in self.sliders:
                sldr.active = True
            self.Kregs = self.slider_group.get_values()

        self.model.set_Kregs(*self.Kregs)
        self.model.update()

        self.poles = []
        for pole in self.model.get_poles():
            pos = self.plane.get_pos_from_point((pole.real, pole.imag))
            self.poles.append(gaussian.Pole(pos, 15, pole.real, pole.imag))

        self.screenshot_imagestr = pg.image.tostring(surface, 'RGB')

        self.draw(surface)

    def draw(self, surface):
        surface.fill(colors.WHITE)
        self.draw_coordlines(surface, self.plane.Re_axis, self.plane.Im_axis)
        self.draw_axes(surface, self.plane.Re_axis, self.plane.Im_axis)

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

                # Animate unstable pole flicker
                signal = self.gen_signal_by_loop(4, 80, forobj='Pole')
                self._draw_aafilled_circle(surface, *pos,
                                           pole.r + round(signal),
                                           colors.ARED)
            elif pole.is_marginal_stable():
                dyn_color = colors.CORAL

            self._draw_aafilled_circle(surface, *pos, pole.r, dyn_color)

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
        self.draw_slider_group(surface, self.slider_group)
        self.draw_checkbox(surface, self.checkbox)
        self.draw_button(surface, self.but_set)

        if self.results is not None:
            self.draw_button(surface, self.but_plot)

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

    def plot(self):
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

    def gen_signal_by_loop(self, amplitude, length, forobj='Pole'):
        self.run_loop_counter()
        if forobj == 'Pole':
            return amplitude * m.sin((self._i_/length) * m.pi)**2
        elif forobj == 'But_Refl':
            return not (self._i_ % 1)
