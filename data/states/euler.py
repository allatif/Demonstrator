import math as m

import pygame as pg
import pygame.gfxdraw
import numpy as np

from .. import pg_init, pg_root, setup_sim

from .. components import color
from .. components import gphysics
from .. components.objects import Cone, Sphere, Ground, Ruler
from .. components.animations import Impulse


class Euler(pg_root._State):
    """This state could represent the actual gameplay phase."""

    index = 0

    def __init__(self, mother=True):
        if mother:
            pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.next = "POLEMAP"
        self.bg_img = pg_init.GFX['bg']

        self.sim = setup_sim.SimData(12000)

        self.ground = Ground(510, self.width, thickness=10)

        self.cone = Cone(basis_length=pg_init.SCALE,
                         basis_center_x=self.width//2,
                         ratio=0.85)

        self.ball = Sphere(radius=round(self.sim.k_k.radius*pg_init.SCALE),
                           mass=self.sim.k_k.mass_sphere,
                           inertia=self.sim.k_k.J,
                           zero_pos_x=self.cone.get_zero_pos())

        self.ruler = Ruler(pos=self.ground.pos+self.ground.w,
                           zero=self.cone.get_zero_pos(),
                           length=self.ground.len)

        self.interference = None
        self.wave = None

        self.physics = None
        self.state_values = (0, 0, 0, 0)
        self.simdone = False
        self.results = None

        self.hudfont = pg.font.SysFont('Consolas', 12)
        self.rulefont = pg.font.SysFont('Liberation Sans', 18)
        self.options = {"Hud position": 'right', "Angle unit": 'rad'}

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.__init__(mother=False)
        self.regs = self.persist["controller"]
        self.sim.set_regs(*self.regs)
        print(self.regs)

        # Reset Euler algorithm
        Euler.index = 0

    def cleanup(self):
        self.done = False
        self.persist["result"] = self.results
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
                self.interference = self._disturbing_func(diff)

                self.wave = Impulse(args=(mouse[0], mouse[1], 8, 2, diff))
                self.wave.start()
            else:
                print('Outside')

    def update(self, surface, mouse):
        self.sim.update()

        A_sys = self.sim.system
        x1, x2, x3, x4 = self.sim.state_vec
        t_vec = self.sim.t_vec

        k = Euler.index

        if self.interference is not None:
            x4[k] += self.interference
        self.interference = None

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

        if abs(x3[k]) > self.deg2rad(30):
            # if ball tilt angle > 30°
            # system stops controlling, controller values set to zero
            self.sim.set_regs(0, 0, 0, 0)

        if abs(x3[k]) > self.deg2rad(60):
            # if ball tilt angle > 60°
            # ball will start falling and shall roll down the cone
            self.ball.falling = True

        self.state_values = (np.float(x1[k]), np.float(x2[k]),
                             np.float(x3[k]), np.float(x4[k]))

        # If-Path for Euler Method
        if not self.ball.falling:
            self.cone.update(np.float(x1[k]))
            self.ball.update(self.cone.get_points('top'),
                             np.float(x3[k]),
                             np.float(x4[k]))

            if k >= self.sim.sim_length-1:
                self.simdone = True
            else:
                k += 1
                Euler.index = k

        # Else-Path for simulating ball drop
        elif self.ball.falling:
            if self.physics is None:
                self.physics = gphysics.gPhysics(cone=self.cone,
                                                 ball=self.ball,
                                                 ground=self.ground)
            self.physics.update()

        self.results = x1[:k], self.rad2deg(x3[:k]), t_vec[:k]
        self.draw(surface)

    def draw(self, surface):
        surface.blit(self.bg_img, pg_init.SCREEN_RECT)
        self.draw_ground(surface)
        self.draw_ruler(surface)
        self.draw_cone(surface, reflection=True)
        self.draw_ball(surface)
        self.draw_hud(surface, 115, 66, pos=self.options["Hud position"])

        if self.wave is not None and not (self.ball.falling or self.simdone):
            self.draw_impulsewave(surface)

        if self.ball.touchdown:
            self.draw_message(surface, 'Game Over')

        if self.simdone:
            self.draw_message(surface, 'Finished')

    def draw_ground(self, surface):
        pg.draw.line(surface, color.BLACK,
                     *self.ground.get_line(), self.ground.w)

    def draw_ruler(self, surface):
        self.draw_trigon_marker(surface)

        text_margin = 25

        scales = self.ruler.get_scales(10, 5, 2, subs=10)
        for scale in scales:
            pg.draw.line(surface, color.BLACK,
                         *scale, self.ruler.scale_w)

        for num, pos_x in self.ruler.get_numbers():
            text = self.rulefont.render(str(num), True, color.BLACK)
            rect = text.get_rect(center=(pos_x+1, self.ruler.pos+text_margin))
            surface.blit(text, rect)

    def draw_trigon_marker(self, surface):
        point_bottom = (self.cone.get_points('top')[0],
                        self.ground.pos + self.ground.w)
        point_left = (self.cone.get_points('top')[0] - (self.ground.w//2),
                      self.ground.pos+1)
        point_right = (self.cone.get_points('top')[0] + (self.ground.w//2),
                       self.ground.pos+1)

        self._draw_aafilled_polygon(surface,
                                    (point_bottom, point_left, point_right),
                                    color.GREY)

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

    def draw_ball(self, surface):
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
            apex_y = self.cone.get_points('top')[1]
            red = color.DRED[0]
            red = red + 5*s
            rgb = (red, 0, 0)

            # shade width
            w = 3

            if s == 0:
                pg.gfxdraw.filled_ellipse(surface, c_x, c_y,
                                          self.ball.r - w*s, r_y - w*s, rgb)

            else:
                offzero = apex_y - c_y - self.ball.r
                change = m.sqrt(1.26*((abs(offzero)/200) + 1))
                lightest_spot_c_x = c_x + round(-10*_x_)
                lightest_spot_c_y = round(change*(apex_y - self.ball.r))
                light_offcenter_y = abs(lightest_spot_c_y - c_y)

                # Value to squeeze elliptical shades in y-direction
                # when lightest spot is off-center
                sqz_y = 2*round((s/((shades-1)*10)) * light_offcenter_y)

                if s == shades-1:
                    c_x = lightest_spot_c_x
                    c_y = lightest_spot_c_y

                gap_x = (lightest_spot_c_x-c_x) / (shades-2)
                gap_y = (lightest_spot_c_y-c_y) / (shades-2)
                pg.gfxdraw.filled_ellipse(surface,
                                          c_x + round(gap_x*s),
                                          c_y + round(gap_y*s),
                                          self.ball.r - w*s,
                                          r_y - w*s - sqz_y,
                                          rgb)

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
        text_margin = 5
        line_margin = 14

        rect = self.render_hud(length, wide, margin, pos)
        pg.gfxdraw.box(surface, rect, color.TRAN200)

        units = ['m', 'm/s', 'rad', 'rad/s']
        SI = True
        if self.options["Angle unit"] == 'deg':
            units = ['m', 'm/s', '°', '°/s']
            SI = False

        for num, value in enumerate(self.state_values):
            value = self.rad2deg(value) if num > 1 and not SI else value
            space = '  ' if value > 0 else ' '
            value_str = f'x{num+1}:{space}{value:.2f} {units[num]}'
            text = self.hudfont.render(value_str, True, color.WHITE)

            surface.blit(text,
                         (rect[0] + text_margin,
                          rect[1] + text_margin + num*line_margin))

    def draw_message(self, surface, text):
        fontname = 'ARCADECLASSIC'
        center = (self.width//2, self.cone.get_points('top')[1]//2)
        msg, rect = self.render_font(text, fontname, 128, color.LRED, center)
        alpha_surface = pg.Surface((rect[2]+12, rect[3]-10), pg.SRCALPHA)
        alpha_surface.fill(color.TRAN150)
        alpha_surface.blit(msg, (8, -3))
        surface.blit(alpha_surface, rect)

    def _disturbing_func(self, intensity):
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
