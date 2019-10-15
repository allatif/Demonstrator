import math as m

import pygame as pg
import pygame.gfxdraw
import matplotlib.pyplot as plt

from .. import pg_init, pg_root, setup_sim

from .. components import color, gaussian
from .. interface import slider_group, slider, button, checkbox


class PoleMap(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.plane = gaussian.Plane(self.width, self.height)
        self.next = "GAME"
        self.sim_init_state = (0, 0, 0, 0.3)
        self.model = setup_sim.StateSpaceModel()
        self.poles = None
        self.results = None

        # self.Kregs = [-2196.6, -4761.2, -51800, -18831]
        self.Kregs = [-1296.6, -3161.2, -31800, -9831]
        # self.Kregs = [-1196.6, -3761.2, -11800, -8831]
        # for testing fall of sphere
        # # self.Kregs = [-9050, -3150, -4800, -9750]

        # Initialize sliders
        self.sliders = []
        slider_ranges = [(0, -10000), (0, -20000), (0, -180000), (0, -60000)]
        for slider_range, val in zip(slider_ranges, self.Kregs):
            self.sliders.append(slider.Slider(val, 2, 200, range_=slider_range,
                                              track_color=color.GREY,
                                              act_filled_color=color.CORAL,
                                              act_thumb_color=color.TOMATO,
                                              act_value_color=color.TOMATO,
                                              dea_filled_color=color.DGREY,
                                              dea_thumb_color=color.BLACK,
                                              dea_value_color=color.LGREY))
        self.slider_group = slider_group \
            .SliderGroup(self.sliders, header_text='Controller Settings',
                         header_size=16)
        self.slider_group.arrange(20, 20)

        # Used checkbox
        # # Checkbox position depends on last slider
        cb_pos_x = self.sliders[len(self.sliders)-1].track.rect[0]
        cb_pos_y = self.sliders[len(self.sliders)-1].track.rect[1] + 20
        self.checkbox = checkbox.CheckBox(16, 2, color.BLACK)
        self.checkbox.set_pos(cb_pos_x, cb_pos_y)
        self.checkbox.set_label('Switch off Controller', margin=5)

        # Used buttons
        self.but_set = button.Button('Settings',
                                     obj_color=color.LBLUE,
                                     hov_color=color.LLBLUE,
                                     text_color=color.WHITE)
        self.but_set.set_pos(self.width-self.but_set.width-15, 10)

        self.but_plot = button.Button('Show Plot',
                                      obj_color=color.LRED,
                                      hov_color=color.LLRED,
                                      text_color=color.WHITE)
        self.but_plot.set_pos(self.but_set.pos[0]-self.but_plot.width-15, 10)
        self.but_plot.activate_reflection()

        self.options = {"Hud position": 'left', "Euler corr": False}
        self.loop_counter = 0

        self.polemap_imagestr = ''

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.next = "GAME"

        self.sim_init_state = self.persist["sim initial state"]
        if "result" in self.persist:
            self.results = self.persist["result"]

    def cleanup(self):
        self.done = False
        self.but_plot.virgin = True
        self.persist["sim initial state"] = self.sim_init_state
        self.persist["controller"] = self.Kregs
        self.persist["control off"] = self.checkbox.checked
        self.persist["bg_image"] = self.polemap_imagestr
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
            if event.key == pg.K_F1:
                self.options["Hud position"] = 'left'
            if event.key == pg.K_F2:
                self.options["Hud position"] = 'right'
            if event.key == pg.K_c:
                self.options["Euler corr"] = not self.options["Euler corr"]
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
        self.slider_group_logic(mouse, self.slider_group)
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

        # Euler method causes a little error per step k when dt is too big
        # Need of correction offset 'corr' to correct marginal stable poles
        crr = 0.0485 if self.options['Euler corr'] else 0.0
        self.poles = []
        for pole in self.model.get_poles():
            pos = self.plane.get_pos_from_point((pole.real+crr, pole.imag))
            self.poles.append(gaussian.Pole(pos, 15, pole.real+crr, pole.imag))

        self.polemap_imagestr = pg.image.tostring(surface, 'RGB')

        self.draw(surface)

    def draw(self, surface):
        surface.fill(color.WHITE)
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

            dyn_color = color.LBLUE
            if pole.is_unstable():
                dyn_color = color.RED

                # Animate unstable pole flicker
                signal = self.gen_signal_by_loop(4, 80, forobj='Pole')
                self._draw_aafilled_circle(surface, *pos,
                                           pole.r + round(signal),
                                           color.ARED)
            elif pole.is_marginal_stable():
                dyn_color = color.CORAL

            self._draw_aafilled_circle(surface, *pos, pole.r, dyn_color)

        self.draw_interface(surface)
        self.draw_hud(surface, 115, 66, pos=self.options["Hud position"])

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
        self.draw_slider_group(surface, self.slider_group)
        self.draw_checkbox(surface, self.checkbox)
        self.draw_button(surface, self.but_set)

        if self.results is not None:
            self.draw_button(surface, self.but_plot)

    def draw_hud(self, surface, length, wide, margin=4, pos='left'):
        text_margin = 5
        line_margin = 14

        rect = self.render_hud(length, wide, margin, pos)
        hudcolor = color.TRAN200

        if self.options["Euler corr"]:
            # Show if option Euler method correction offset is activated
            msg = '*Imaginary axis offset'
            text = self.render_font(msg, 'Liberation Sans', 14, color.DBLUE)
            var_x_pos = rect[0]+length+2 if pos == 'left' else rect[0]-110
            surface.blit(text, (var_x_pos, rect[1]+wide-18))

            hudcolor = color.A200DDBLUE

        pg.gfxdraw.box(surface, rect, hudcolor)

        for num, pole in enumerate(self.poles):
            pole_str = f'{pole}'
            text_color = color.LRED if pole.is_unstable() else color.WHITE
            text = self.hudfont.render(pole_str, True, text_color)

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
            plt.ylabel('Velocity [m/s]')
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
