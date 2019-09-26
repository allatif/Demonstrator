import math as m

from .. import pg_init

GRAVITY = 9.81


class gPhysics:

    def __init__(self, **kwargs):
        self.cone = kwargs.get('cone', None)
        self.ball = kwargs.get('ball', None)
        self.ground = kwargs.get('ground', None)

        self.slope = None
        self.coast = None

    def update(self):
        if not self.ball.touchdown:
            if self.slope is None:
                self.slope = SlopeModel(self.ball.get_center(),
                                        self.ball.ang,
                                        self.ball.ang_vel,
                                        self.ball.get_props(),
                                        self.cone.get_basis_angle())
            self.slope.update()
            x, y, ang, ang_vel = self.slope.generate()
            self.ball.fall(x, y, ang, ang_vel, self.ground.pos)

        elif self.ball.touchdown and not self.ball.stopped:
            if self.coast is None:
                self.coast = CoastModel(self.ball.get_center(),
                                        self.ball.ang,
                                        self.ball.ang_vel,
                                        self.ball.get_props())
            self.coast.update()
            x, ang = self.coast.generate()
            self.ball.roll(x, ang)
            print(self.ball.get_center())

            if self.coast.is_stillstand():
                self.ball.stopped = True

    def check_collision(self):
        if self.cone is not None:
            lef_x, lef_y, rig_x, rig_y, top_x, top_y = self.cone.get_coords()
            slope_lef = (lef_x - top_x) / (lef_y - top_y)
            slope_rig = -slope_lef

        if self.ball is not None and self.cone is not None:
            base_y = lef_y
            for y in range(top_y, base_y):
                x_lef = slope_lef*(y-top_y) + top_x
                x_rig = slope_rig*(y-top_y) + top_x
                if (self.ball.inside((x_lef, y))
                        or self.ball.inside((x_rig, y))):
                    return True
                return False
        return


class _State:

    counter = 0

    def __init__(self, start_pos, start_ang, start_ang_vel, ball_props):
        # Ball states
        self.x0, self.y0 = start_pos
        self.ang0 = start_ang
        self.ang_v0 = start_ang_vel
        # Ball properties - radius, mass, inertia
        self.ball_r, self.ball_m, self.ball_J = ball_props

        self.t = 0
        self.fps = 100
        self.scale = pg_init.SCALE

        self.real_r = self.ball_r / self.scale

        _State.counter = 0

    def update(self):
        self.t = _State.counter*(1/self.fps)
        _State.counter += 1


class SlopeModel(_State):

    def __init__(self, start_pos, start_ang, start_ang_vel, ball_props,
                 slope_angle):
        _State.__init__(self, start_pos, start_ang, start_ang_vel, ball_props)
        self.slope_angle = slope_angle

    def generate(self):
        accel, ang_accel = self._calc_ball_accel()

        travel = 0.5*accel*self.t**2 + abs(self.ang_v0*self.real_r)*self.t

        # Direction switch depending on angle of dip
        switch = {'left': -1, 'right': 1}
        key = 'left' if self.ang0 < 0 else 'right'
        x = switch[key]*m.cos(self.slope_angle)*travel*self.scale + self.x0
        y = m.sin(self.slope_angle)*travel*self.scale + self.y0

        accel_rot = 0.5 * ang_accel * self.t**2
        if self.ang_v0 < 0:
            ang = -accel_rot + self.ang_v0*self.t + self.ang0
            ang_vel = -ang_accel*self.t + self.ang_v0
        else:
            ang = accel_rot + self.ang_v0*self.t + self.ang0
            ang_vel = ang_accel*self.t + self.ang_v0

        return round(x), round(y), ang, ang_vel

    def _calc_ball_accel(self):
        angular_accel = (
            self.ball_m * GRAVITY * self.real_r * m.sin(self.slope_angle)
        ) / self.ball_J
        accel = angular_accel * self.real_r
        return accel, angular_accel


class CoastModel(_State):

    def __init__(self, start_pos, start_ang, start_ang_vel, ball_props):
        _State.__init__(self, start_pos, start_ang, start_ang_vel, ball_props)
        self.ang_vel = None
        self.ang_vel_1_2 = []
        self.stillstand = False

    def generate(self):
        c_friction = 1.1

        if self.ang_v0 < 0:
            ang_decel = ((self.ball_m*GRAVITY*c_friction*self.real_r)
                         / self.ball_J)
        else:
            ang_decel = -((self.ball_m*GRAVITY*c_friction*self.real_r)
                          / self.ball_J)

        decel_rot = 0.5 * ang_decel * self.t**2

        ang = decel_rot + self.ang_v0*self.t + self.ang0

        self.ang_vel = decel_rot*self.t + self.ang_v0
        x = self.ang_vel * self.real_r * self.t * self.scale + self.x0
        print(self.ang_vel)

        return round(x), ang

    def is_stillstand(self):
        self.ang_vel_1_2.append(abs(self.ang_vel))
        if len(self.ang_vel_1_2) == 2:
            print(self.ang_vel_1_2)
            if self.ang_vel_1_2[1] > self.ang_vel_1_2[0]:
                return True
            self.ang_vel_1_2 = []
