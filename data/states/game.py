import math as m

import pygame as pg
import pygame.gfxdraw
import numpy as np

from .. import pg_init, pg_root, setup_sim, euler

from .. components import colors
from .. components import gphysics
from .. components.mousecontrol import MouseControl
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
        self.bg_img = pg_init.GFX['bg']

        # Initialize Control Objects
        self.control_object = None
        self.force_records = []
        self.user = MouseControl(sensibility=1000)
        self.agent = Agent()

        # Initialize Dynamik Model
        self.sim = setup_sim.SimData(120_000)
        if hasattr(self, 'sim_init_state'):
            self.sim = setup_sim.SimData(120_000, self.sim_init_state)
            self.agent.observe(np.array([*self.sim_init_state]))

        self.model = setup_sim.StateSpaceModel()

        # Initialize Game Objects
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
                           length=self.ground.len, marker_color=colors.ORANGE)
        self.ruler.set_scales(10, 5, scale_w=2, subs=10)
        self.ruler.set_labels(top=25, size=18)

        self.interference_load = None
        self.wave = None
        self.physics = None
        self.simover = False
        self.predone = False
        self.results = None
        self.state_values = (0, 0, 0, 0)

        self.options = {"Hud position": 'right', "Angle unit": 'rad'}

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)

        if self.previous == 'POLEMAP':
            self.Kregs = self.persist["controller"]
            self.mode = self.persist["mode"]
            self.next = "POLEMAP"
        elif self.previous == 'NEURO':
            self.Kregs = (0, 0, 0, 0)
            self.mode = 'agent'
            self.agent_model = self.persist["selected model"]
            self.next = "NEURO"

        self.sim_ref_state = self.persist["sim reference state"]
        self.sim_init_state = self.persist["sim initial state"]
        self.euler_ministeps = self.persist["euler ministeps"]
        self.frame_step = self.euler_ministeps

        self.__init__(mother=False)

        self.model.set_Kregs(*self.Kregs)
        self.model.update()

        self.ruler.marker.set(self.sim_ref_state[0])

        if self.mode == 'user':
            print(" -- User in control now -- ")
        elif self.mode == 'ss_controller':
            print(self.Kregs)
        elif self.mode == 'agent':
            self.agent.load_model(self.agent_model)
            print(" -- Agent in control now -- ")
            print("Loaded TensorFlow model", self.agent_model)

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
            if event.key == pg.K_LEFT:
                self.ruler.marker.click(0)
            if event.key == pg.K_RIGHT:
                self.ruler.marker.click(1)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if not self.ball.falling:
                self.user.input = True

            if self.ball.mouseover:
                diff = self.user.mouse[0] - self.cone.get_center_x()
                self.interference_load = self._disturbing_func(diff)

                self.wave = Impulse(args=(self.user.mouse[0],
                                          self.user.mouse[1],
                                          8, 2, diff))
                self.wave.start()

            if self.ruler.marker.mouseover:
                self.ruler.marker.grab()

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.user.input = False

            if self.ruler.marker.grabbed:
                self.ruler.marker.release()
                self.ruler.marker.snap()

    def mouse_logic(self, mouse):
        self.hover_object_logic(mouse, self.ball)
        if self.ruler.marker.inside(mouse):
            self.ruler.marker.mouseover = True
        else:
            self.ruler.marker.mouseover = False

        if self.ruler.marker.grabbed:
            self.ruler.marker.slide(mouse)

        self.user.update(mouse)

    def update(self, surface):
        if self.mode == 'user':
            self.control_object = self.user
        elif self.mode == 'agent':
            self.agent.update()
            self.control_object = self.agent

        # Update Reference State x via ruler marker
        self.ruler.marker.update()
        self.sim_ref_state = self._update_reference_state()

        # Gathering variables for State Space Euler
        A_matrix = self.model.system
        B_matrix = self.model.B
        x1_vec, x2_vec, x3_vec, x4_vec = self.sim.state_vec
        t_vec = self.sim.t_vec

        interference = 0.0
        if self.interference_load is not None:
            interference = self.interference_load
            self.interference_load = None

        self.euler_thread = euler.EulerThread(args=(A_matrix, B_matrix,
                                                    self.sim.state_vec, t_vec,
                                                    self.static_fps,
                                                    self.euler_ministeps,
                                                    Game.step,
                                                    self.control_object,
                                                    interference,
                                                    self.sim_ref_state))
        self.euler_thread.start()
        x1, x2, x3, x4, self.simover = self.euler_thread.join()
        self.agent.observe(np.array([x1, x2, x3, x4]))

        if abs(x3) > m.radians(20):
            # If ball tilt angle > 20°
            # System stops controlling, controller values set to zero
            self.model.set_Kregs(0, 0, 0, 0)
            self.model.update()

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
                Game.step += self.frame_step

            if self.control_object is not None:
                self.force_records.append(self.control_object.force)

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
        if self.control_object is not None:
            self.draw_force_hud(surface, 160, 36)

        if self.wave is not None and not (self.ball.falling or self.simover):
            self.draw_impulsewave(surface)

        if self.ball.touchdown:
            self.draw_message(surface, 'Game Over')

        if self.simover:
            self.draw_message(surface, 'Finished')

    def draw_ground(self, surface):
        pg.draw.line(surface, colors.BLACK,
                     *self.ground.get_line(), self.ground.w)

    def draw_ruler(self, surface):
        self.draw_trigon_marker(surface)

        for scale in self.ruler.scales:
            pg.draw.line(surface, colors.BLACK, *scale, self.ruler.scale_w)

        for label in self.ruler.num_labels:
            label.cache_font(label.text, 'Liberation Sans', label.height,
                             colors.BLACK, center=(label.pos[0], label.pos[1]))
            surface.blit(label.font_cache[0], label.font_cache[1])

        if self.mode is not 'user':
            self.draw_reference_marker(surface)

    def draw_trigon_marker(self, surface):
        point_bottom = (self.cone.get_points('top')[0],
                        self.ground.pos + self.ground.w)
        point_left = (self.cone.get_points('top')[0] - (self.ground.w//2),
                      self.ground.pos+1)
        point_right = (self.cone.get_points('top')[0] + (self.ground.w//2),
                       self.ground.pos+1)

        self._draw_aafilled_polygon(surface,
                                    (point_bottom, point_left, point_right),
                                    colors.GREY)

    def draw_reference_marker(self, surface):
        # Draws a pentagon like a house shape (trigon + rectangle)
        marker = self.ruler.marker
        point_top = marker.x, marker.y
        point_a = marker.rec_x, marker.rec_y
        point_b = marker.rec_x + marker.width, marker.rec_y
        point_c = marker.rec_x, marker.rec_y + marker.length
        point_d = marker.rec_x + marker.width, marker.rec_y + marker.length
        self._draw_aafilled_polygon(surface, (point_top, point_a, point_c,
                                              point_d, point_b), marker.color)
        # Draw shadow
        pg.draw.aalines(surface, colors.ORANGE_PACK['shadow'], False,
                        (point_top, point_b, point_d))

    def draw_cone(self, surface, reflection=True):
        # Real location of cone
        _x_ = self.cone.loc

        # Antialiased outline
        pg.gfxdraw.aatrigon(surface, *self.cone.get_coords(), colors.GREY)

        if not reflection:
            pg.draw.polygon(surface, colors.GREY, self.cone.get_points())
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
                            self.ball.r, colors.DRED)

        # Shading
        shades = 21
        for s in range(shades):
            r_y = self.ball.r
            c_x, c_y = self.ball.get_center()
            apex_y = self.cone.get_points('top')[1]
            red = colors.DRED[0]
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
                                    colors.DGREY)

    def draw_impulsewave(self, surface):
        if self.wave.running:
            alpha_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
            pg.draw.circle(alpha_surface, self.wave.dynamic_color,
                           self.wave.get_center(), self.wave.radius,
                           self.wave.width)
            surface.blit(alpha_surface, (0, 0))

    def draw_hud(self, surface, width, height, margin=4, pos='right'):
        text_margin = 5
        line_margin = 14

        rect = self.render_hud(width, height, margin, pos)
        pg.gfxdraw.box(surface, rect, colors.TRAN200)

        units = ['m', 'm/s', 'rad', 'rad/s']
        SI = True
        if self.options["Angle unit"] == 'deg':
            units = ['m', 'm/s', '°', '°/s']
            SI = False

        for num, value in enumerate(self.state_values):
            value = m.degrees(value) if num > 1 and not SI else value
            space = '  ' if value >= 0 else ' '
            value_str = f'x{num+1}:{space}{value:.2f} {units[num]}'
            text = self.hudfont.render(value_str, True, colors.WHITE)

            surface.blit(text,
                         (rect[0] + text_margin,
                          rect[1] + text_margin + num*line_margin))

    def draw_force_hud(self, surface, width, height,
                       update_rate=10, margin=4, pos='center'):
        frames_per_update = self.static_fps // update_rate

        text_margin_top = 4
        text_margin_left = 8

        rect = self.render_hud(width, height, margin, pos)
        pg.gfxdraw.box(surface, rect, colors.TRAN200)

        fontname = 'Consolas'
        fontsize = 32
        if self._i_ % frames_per_update == 0:
            self._temp_0 = self.control_object.force
        value = self._temp_0

        space = '  ' if value >= 0 else ' '
        text_color = colors.TOMATO if value >= 0 else colors.CYAN
        value_str = f'F{space}{value}'
        text = self.render_font(value_str, fontname, fontsize, text_color)
        surface.blit(text, (rect[0]+text_margin_left, rect[1]+text_margin_top))
        self.run_loop_counter()

    def draw_message(self, surface, text):
        fontname = 'ARCADECLASSIC'
        center = (self.width//2, self.cone.get_points('top')[1]//2)
        msg, rect = self.render_font(text, fontname, 128, colors.LRED, center)
        alpha_surface = pg.Surface((rect[2]+12, rect[3]-10), pg.SRCALPHA)
        alpha_surface.fill(colors.TRAN150)
        alpha_surface.blit(msg, (8, -3))
        surface.blit(alpha_surface, rect)

    def _disturbing_func(self, intensity):
        return -intensity*1.0e-2

    def _update_reference_state(self):
        return self.ruler.marker.value, self.sim_ref_state[1]
