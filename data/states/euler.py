import math as m

import pygame as pg
import pygame.gfxdraw
import numpy as np

from .. import pg_init, pg_root, setup_sim

from .. components import color
from .. components import gphysics
from .. components.objects import Cone, Sphere, Ground
from .. components.animations import Impulse


class Euler(pg_root._State):
    """This state could represent the actual gameplay phase."""

    index = 0

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.next = "POLEMAP"
        self.bg_img = pg_init.GFX['bg']

        self.sim = setup_sim.SimData(20000)
        self.interference = None
        self.ground = Ground(510, self.width, thickness=10)
        self.cone = Cone(basis_length=200,
                         basis_center_x=self.width//2,
                         ratio=0.85)
        self.ball = Sphere(radius=round(self.sim.k_k.radius*pg_init.SCALE),
                           mass=self.sim.k_k.mass_sphere,
                           inertia=self.sim.k_k.J,
                           zero_pos_x=self.cone.get_zero_pos())
        self.wave = None

        self.physics = None

        self.state_values = (0, 0, 0, 0)
        self.fail = False

        self.hudfont = pg.font.SysFont('Consolas', 12)
        self.options = {"Hud position": 'right', "Angle unit": 'rad'}

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.regs = self.persist["controller"]
        print(self.regs)

        # Reset Euler algorithm
        Euler.index = 0

    def cleanup(self):
        self.done = False
        self.fail = False
        self.ball.touchdown = False
        self.physics = None
        return self.persist

    def get_event(self, event, mouse):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
            if event.key == pg.K_F1:
                self.options["Hud position"] = 'left'
            if event.key == pg.K_F2:
                self.options["Hud position"] = 'right'
            if event.key == pg.K_F3:
                if self.options["Angle unit"] == 'rad':
                    self.options["Angle unit"] = 'deg'
                else:
                    self.options["Angle unit"] = 'rad'

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.ball.inside(mouse):
                diff = mouse[0] - self.cone.get_center_x()
                self.interference = self.disturbing_func(diff)

                self.wave = Impulse(args=(mouse[0], mouse[1], 8, 2, diff))
                self.wave.start()
            else:
                print('Outside')

    def update(self, surface, mouse):
        self.sim.set_regs(*self.regs)
        self.sim.update()

        A_sys = self.sim.system
        x1, x2, x3, x4 = self.sim.state_vec
        t_vec = self.sim.t_vec

        k = Euler.index

        if self.interference is not None:
            x4[k] += self.interference
        self.interference = None

        if abs(x3[k]) > self.deg2rad(40):
            self.fail = True

        # dt = 1 / pg_init.FPS
        dt = 0.01

        # Euler Method
        x1[k+1] = x1[k] + dt*(
            x1[k]*A_sys[0, 0] + x2[k]*A_sys[0, 1]
            + x3[k]*A_sys[0, 2] + x4[k]*A_sys[0, 3]
        )
        x2[k+1] = x2[k] + dt*(
            x1[k]*A_sys[1, 0] + x2[k]*A_sys[1, 1]
            + x3[k]*A_sys[1, 2] + x4[k]*A_sys[1, 3]
        )
        x3[k+1] = x3[k] + dt*(
            x1[k]*A_sys[2, 0] + x2[k]*A_sys[2, 1]
            + x3[k]*A_sys[2, 2] + x4[k]*A_sys[2, 3]
        )
        x4[k+1] = x4[k] + dt*(
            x1[k]*A_sys[3, 0] + x2[k]*A_sys[3, 1]
            + x3[k]*A_sys[3, 2] + x4[k]*A_sys[3, 3]
        )

        t_vec[k+1] = t_vec[k] + dt

        self.state_values = (np.float(x1[k]), np.float(x2[k]),
                             np.float(x3[k]), np.float(x4[k]))

        # If-Path for Euler Method
        if not self.fail:
            self.cone.update(np.float(x1[k]))
            self.ball.update(self.cone.get_points('top'), np.float(x3[k]))
            k += 1
            Euler.index = k

        # Else-Path for simulating ball drop
        elif self.fail and not self.ball.touchdown:
            if self.physics is None:
                self.physics = gphysics.gPhysics(trigon=self.cone,
                                                 circle=self.ball,
                                                 states=self.state_values)
            self.physics.update()
            x, y = self.physics.gen_slope()
            ang = self.physics.gen_slope_rot()
            self.ball.fall(x, y, ang, self.ground.pos)

        self.draw(surface)

    def draw(self, surface):
        surface.blit(self.bg_img, pg_init.SCREEN_RECT)
        self.draw_ground(surface)
        self.draw_cone(surface, reflection=True)
        self.draw_ball(surface, reflection=False)
        self.draw_hud(surface, 115, 66, pos=self.options["Hud position"])

        if self.wave is not None and not self.fail:
            self.draw_impulsewave(surface)

    def draw_ground(self, surface):
        pg.draw.line(surface, color.BLACK,
                     *self.ground.get_line(), self.ground.w)

    def draw_cone(self, surface, reflection=True):
        # real location of cone
        _x_ = self.cone.loc

        # antialiased outline
        pg.gfxdraw.aatrigon(surface, *self.cone.get_coords(), color.GREY)

        if not reflection:
            pg.draw.polygon(surface, color.GREY, self.cone.get_points())
        else:
            for s in range(40):
                grey = 100
                grey = grey * m.sin(m.pi*((s + _x_*4)/40))**3 + 75
                if grey < 0:
                    grey = 0

                rgb = (grey, grey, grey)
                pg.draw.polygon(surface, rgb,
                                ((self.cone.get_points('left')[0] + s*5,
                                  self.cone.get_points('left')[1]),
                                 self.cone.get_points('right'),
                                 self.cone.get_points('top')))

    def draw_ball(self, surface, reflection=False):
        # real location of ball
        _x_ = self.ball.loc

        # antialiased outline
        pg.gfxdraw.aacircle(surface, *self.ball.get_center(),
                            self.ball.r, color.DRED)

        # shading
        shades = 21
        for s in range(shades):
            r_y = self.ball.r
            c_x, c_y = self.ball.get_center()
            red = color.DRED[0]
            red = red + 5*s
            rgb = (red, 0, 0)

            # shade width
            w = 3

            if s == 0:
                pg.gfxdraw.filled_ellipse(surface, c_x, c_y,
                                          self.ball.r - w*s, r_y - w*s, rgb)

            else:
                lightest_spot_c_x = c_x + round(-14*_x_)
                lightest_spot_c_y = c_y + round(-14*_x_*m.sin(self.ball.ang))

                if s == shades-1:
                    c_x = lightest_spot_c_x
                    c_y = lightest_spot_c_y

                gap_x = (lightest_spot_c_x-c_x) / (shades-2)
                gap_y = (lightest_spot_c_y-c_y) / (shades-2)
                pg.gfxdraw.filled_ellipse(surface,
                                          c_x + round(gap_x*s),
                                          c_y + round(gap_y*s),
                                          self.ball.r - w*s, r_y - w*s, rgb)

        if reflection:
            # reflection as an elliptical shape
            radius_x = 24
            radius_y = 22
            center_x = int(self.cone.get_points('top')[0]) - round(_x_*40)
            center_y = int(self.cone.get_points('top')[1]) - self.ball.r//2

            alpha_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
            for r in range(radius_y):
                alpha = 168 * m.sqrt(r/radius_y)
                rgba = (255, 255, 255, alpha)
                dyn_radius_x = radius_x - r - int(abs(_x_*3))
                dyn_radius_y = radius_y - r
                if dyn_radius_x < 1:
                    dyn_radius_x = 1

                pg.gfxdraw.filled_ellipse(alpha_surface,
                                          center_x, center_y,
                                          dyn_radius_x, dyn_radius_y,
                                          rgba)
            surface.blit(alpha_surface, (0, 0))

        # pg.draw.line(surface, color.DGREY, *self.ball.get_equator_line(10)
        self._draw_aafilled_polygon(surface,
                                    self.ball.get_equator_tape(width=10),
                                    color.DGREY)

    def draw_impulsewave(self, surface):
        if self.wave.running:
            alpha_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
            pg.draw.circle(alpha_surface, self.wave.dynamic_color,
                           self.wave.get_center(), self.wave.radius,
                           self.wave.width)
            surface.blit(alpha_surface, (0, 0))

    def draw_hud(self, surface, length, wide, margin=4, pos='right'):
        rect = (self.width//2, self.height//2, length, wide)
        text_margin = 5
        line_margin = 14
        units = ['m', 'm/s', 'rad', 'rad/s']
        SI = True
        if self.options["Angle unit"] == 'deg':
            units = ['m', 'm/s', '°', '°/s']
            SI = False

        for num, value in enumerate(self.state_values):
            if num > 1 and not SI:
                value = self.rad2deg(value)

            value_str = f'x{num+1}: {value:.2f} {units[num]}'
            if value > 0:
                value_str = f'x{num+1}:  {value:.2f} {units[num]}'
            text = self.hudfont.render(value_str, True, color.WHITE)

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

    def disturbing_func(self, intensity):
        return -intensity*1.0e-2

    @staticmethod
    def _draw_aafilled_polygon(surface, points, color):
        pg.gfxdraw.aapolygon(surface, points, color)
        pg.gfxdraw.filled_polygon(surface, points, color)

    @staticmethod
    def deg2rad(deg):
        return deg * (m.pi/180)

    @staticmethod
    def rad2deg(rad):
        return (rad*180) / m.pi
