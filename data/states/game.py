import math as m

import pygame as pg
import pygame.gfxdraw
import numpy as np

from .. import pg_init, pg_root, setup_sim, euler

from .. components import color
from .. components import gphysics
from .. components import mousecontrol
from .. components.objects import Cone, Sphere, Ground, Ruler
from .. components.animations import Impulse
from .. components.rl.agent import Agent


class Game(pg_root._State):
    """This state could represent the actual gameplay phase."""

    step = 0

    def __init__(self, mother=True):
        if mother:
            pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.next = "POLEMAP"
        self.bg_img = pg_init.GFX['bg']

        self.sim = setup_sim.SimData(120_000)
        if hasattr(self, 'sim_init_state'):
            self.sim = setup_sim.SimData(120_000, self.sim_init_state)
            self.obs = np.array([*self.sim_init_state])

        self.model = setup_sim.StateSpaceModel()
        self.euler_stepsize = 0.001

        # 0.01 for 100 fps
        self.big_step = round(0.01 / self.euler_stepsize)

        # Initialize Objects
        self.ground = Ground(510, self.width, thickness=10)

        self.cone = Cone(basis_length=pg_init.SCALE,
                         basis_center_x=self.width//2,
                         ratio=0.85)

        self.ball = Sphere(radius=round(self.model.k_k.radius*pg_init.SCALE),
                           mass=self.model.k_k.mass_sphere,
                           inertia=self.model.k_k.J,
                           zero_pos_x=self.cone.get_zero_pos())

        self.ruler = Ruler(pos=self.ground.pos+self.ground.w,
                           zero=self.cone.get_zero_pos(),
                           length=self.ground.len)
        self.ruler.set_scales(10, 5, scale_w=2, subs=10)
        self.ruler.set_labels(top=25, size=18)
        # print(self.ruler.scales)

        self.user = mousecontrol.MouseControl(2000)
        self.agent = Agent()
        self.agent.load_model("sphere_cone_rl_pg.h5")

        self.interference_load = None
        self.wave = None
        self.physics = None
        self.state_values = (0, 0, 0, 0)
        self.simover = False
        self.predone = False
        self.results = None

        self.options = {"Hud position": 'right', "Angle unit": 'rad'}

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.sim_ref_state = self.persist["sim reference state"]
        self.sim_init_state = self.persist["sim initial state"]
        self.__init__(mother=False)
        self.Kregs = self.persist["controller"]
        self.user_cont = self.persist["control off"]
        if self.user_cont:
            print(" -- User in control now -- ")
        print(self.Kregs)

        # Reset Euler algorithm
        Game.step = 0

    def cleanup(self):
        self.done = False
        self.persist["result"] = self.results
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.predone = True
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
            self.user.input = True

            if self.ball.mouseover:
                diff = self.user.mouse[0] - self.cone.get_center_x()
                self.interference_load = self._disturbing_func(diff)

                self.wave = Impulse(args=(self.user.mouse[0],
                                          self.user.mouse[1],
                                          8, 2, diff))
                self.wave.start()

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.user.input = False

    def mouse_logic(self, mouse):
        self.hover_object_logic(mouse, self.ball)
        self.user.update(mouse)

    def update(self, surface):
        self.model.update()
        self.model.set_Kregs(*self.Kregs)

        # Gathering variables for State Space
        A_matrix = self.model.system
        B_matrix = self.model.B
        x1_vec, x2_vec, x3_vec, x4_vec = self.sim.state_vec
        t_vec = self.sim.t_vec

        interference = 0.0
        if self.interference_load is not None:
            interference = self.interference_load
            self.interference_load = None

        force = self.agent.act(self.obs)

        self.euler_thread = euler.EulerThread(args=(A_matrix, B_matrix,
                                                    self.sim.state_vec, t_vec,
                                                    self.euler_stepsize,
                                                    Game.step,
                                                    None,
                                                    interference,
                                                    self.sim_ref_state))
        self.euler_thread.start()
        x1, x2, x3, x4, self.simover = self.euler_thread.join()
        self.obs = np.array([x1, x2, x3, x4])

        """
        if abs(x3) < m.radians(0.5) and abs(x1) < 0.025:
            # If ball approaching idle state,
            # that means tilt angle smaller than 0.5°
            # and x position close to zero,
            # system stops controlling
            # That shall simulate interference and inaccuracy
            self.model.set_Kregs(0, 0, 0, 0)
        """

        if abs(x3) > m.radians(30):
            # If ball tilt angle > 30°
            # System stops controlling, controller values set to zero
            self.model.set_Kregs(0, 0, 0, 0)

        if abs(x3) > m.radians(60):
            # If ball tilt angle > 60°
            # Ball will start falling and shall roll down the cone
            self.ball.falling = True

        self.state_values = (np.float(x1), np.float(x2),
                             np.float(x3), np.float(x4))

        # If-Path for Euler Method
        if not self.ball.falling:
            self.cone.update(np.float(x1))
            self.ball.update(self.cone.get_points('top'),
                             np.float(x3),
                             np.float(x4))

            if not self.simover:
                Game.step += self.big_step

        # Else-Path for simulating ball drop
        elif self.ball.falling:
            if self.physics is None:
                self.physics = gphysics.gPhysics(cone=self.cone,
                                                 ball=self.ball,
                                                 ground=self.ground)
            self.physics.update()

        # When event key [ESC]
        # Before state is going to close it will save the results
        if self.predone:
            result_vec_len = self.sim.sim_length if self.simover else Game.step
            self.results = (x2_vec[:result_vec_len],
                            np.degrees(x3_vec[:result_vec_len]),
                            t_vec[:result_vec_len])
            self.done = True

        self.draw(surface)

    def draw(self, surface):
        surface.blit(self.bg_img, pg_init.SCREEN_RECT)
        self.draw_ground(surface)
        self.draw_ruler(surface)
        self.draw_cone(surface, reflection=True)
        self.draw_ball(surface)
        self.draw_hud(surface, 115, 66, pos=self.options["Hud position"])

        if self.wave is not None and not (self.ball.falling or self.simover):
            self.draw_impulsewave(surface)

        if self.ball.touchdown:
            self.draw_message(surface, 'Game Over')

        if self.simover:
            self.draw_message(surface, 'Finished')

    def draw_ground(self, surface):
        pg.draw.line(surface, color.BLACK,
                     *self.ground.get_line(), self.ground.w)

    def draw_ruler(self, surface):
        self.draw_trigon_marker(surface)

        for scale in self.ruler.scales:
            pg.draw.line(surface, color.BLACK, *scale, self.ruler.scale_w)

        for label in self.ruler.num_labels:
            label.cache_font(label.text, 'Liberation Sans', label.height,
                             color.BLACK, center=(label.pos[0], label.pos[1]))
            surface.blit(label.font_cache[0], label.font_cache[1])

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
        # Real location of cone
        _x_ = self.cone.loc

        # Antialiased outline
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
        # Real location of ball
        _x_ = self.ball.loc

        # Antialiased outline
        pg.gfxdraw.aacircle(surface, *self.ball.get_center(),
                            self.ball.r, color.DRED)

        # Shading
        shades = 21
        for s in range(shades):
            r_y = self.ball.r
            c_x, c_y = self.ball.get_center()
            apex_y = self.cone.get_points('top')[1]
            red = color.DRED[0]
            red = red + 5*s
            rgb = (red, 0, 0)

            # Shade width
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
            value = m.degrees(value) if num > 1 and not SI else value
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
