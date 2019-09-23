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
        self.ball = Sphere(
            radius=round(self.sim.k_k.radius*pg_init.SCALE),
            mass=self.sim.k_k.mass_sphere,
            inertia=self.sim.k_k.J
        )
        self.wave = None
        self.fail = False
        self.physics = None

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.regs = self.persist["controller"]
        print(self.regs)

        # Reset Euler algorithm
        Euler.index = 0

    def cleanup(self):
        self.done = False
        self.fail = False
        self.physics = None
        return self.persist

    def get_event(self, event, mouse):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.ball.inside(mouse):
                diff = mouse[0] - self.cone.basis_c_x
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

        if not self.fail:
            k += 1
            self.draw(surface, np.float(x1[k]), np.float(x3[k]))
            Euler.index = k

        elif self.fail and not self.ball.touchdown:
            if self.physics is None:
                self.physics = gphysics.gPhysics(
                    trigon=self.cone,
                    circle=self.ball,
                    states=(np.float(x1[k]), np.float(x2[k]),
                            np.float(x3[k]), np.float(x4[k]))
                )
            self.physics.update()

            self.draw(surface, np.float(x1[k]), self.physics.gen_slope_rot())

    def draw(self, surface, x1, x3):
        surface.blit(self.bg_img, pg_init.SCREEN_RECT)
        self.draw_ground(surface)

        self.cone.update()
        self.cone.move(x1)
        self.draw_cone(surface, x1, reflection=True)

        if not self.fail:
            self.ball.update(self.cone.get_points('top'), x3)
        elif self.fail:
            x, y = self.physics.gen_slope()
            print(self.physics.check_collision())
            self.ball.fall(x, y, self.ground.pos)

        self.draw_ball(surface, x1, x3, reflection=False)

        if self.wave is not None:
            self.draw_impulsewave(surface)

    def draw_ground(self, surface):
        pg.draw.line(surface, color.BLACK,
                     *self.ground.get_line(), self.ground.w)

    def draw_cone(self, surface, x1, reflection=True):
        # antialiased outline
        pg.gfxdraw.aatrigon(surface, *self.cone.get_coords(), color.GREY)

        if not reflection:
            pg.draw.polygon(surface, color.GREY, self.cone.get_points())
        else:
            for s in range(40):
                grey = 100
                grey = grey * m.sin(m.pi*((s + x1*4)/40))**3 + 75
                if grey < 0:
                    grey = 0

                rgb = (grey, grey, grey)
                pg.draw.polygon(surface, rgb,
                                ((self.cone.get_points('left')[0] + s*5,
                                  self.cone.get_points('left')[1]),
                                 self.cone.get_points('right'),
                                 self.cone.get_points('top')))

    def draw_ball(self, surface, x1, x3, reflection=False):
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
                lightest_spot_c_x = c_x + round(-12*x1)
                lightest_spot_c_y = c_y + round(-12*x1*m.sin(x3))

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
            center_x = int(self.cone.get_points('top')[0]) - round(x1*40)
            center_y = int(self.cone.get_points('top')[1]) - self.ball.r//2

            alpha_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
            for r in range(radius_y):
                alpha = 168 * m.sqrt(r/radius_y)
                rgba = (255, 255, 255, alpha)
                dyn_radius_x = radius_x - r - int(abs(x1*3))
                dyn_radius_y = radius_y - r
                if dyn_radius_x < 1:
                    dyn_radius_x = 1

                pg.gfxdraw.filled_ellipse(alpha_surface,
                                          center_x, center_y,
                                          dyn_radius_x, dyn_radius_y,
                                          rgba)
            surface.blit(alpha_surface, (0, 0))

        # pg.draw.line(surface, color.DGREY, *self.ball.get_equator_line(x3), 10)
        self._draw_aafilled_polygon(surface,
                                    self.ball.get_equator_tape(x3, width=10),
                                    color.DGREY)

    def draw_impulsewave(self, surface):
        if self.wave.running:
            alpha_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
            pg.draw.circle(alpha_surface, self.wave.dynamic_color,
                           self.wave.get_center(), self.wave.radius,
                           self.wave.width)
            surface.blit(alpha_surface, (0, 0))

    def disturbing_func(self, intensity):
        return -intensity*1.0e-2

    @staticmethod
    def _draw_aafilled_polygon(surface, points, color):
        pg.gfxdraw.aapolygon(surface, points, color)
        pg.gfxdraw.filled_polygon(surface, points, color)

    @staticmethod
    def deg2rad(deg):
        return deg * (m.pi/180)
