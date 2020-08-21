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
            x, ang, ang_Vel = self.coast.generate()
            self.ball.roll(x, ang)

            if self.coast.is_stillstand(ang_Vel):
                self.ball.stopped = True


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
        self.ang_vel_1_2 = []
        self.stillstand = False

    def generate(self):
        c_friction = 0.1

        # Reduction of ang_vel due to touchdown
        R = 0.4

        if self.ang_v0 < 0:
            ang_decel = ((self.ball_m*GRAVITY*c_friction*self.real_r)
                         / self.ball_J)
        else:
            ang_decel = -((self.ball_m*GRAVITY*c_friction*self.real_r)
                          / self.ball_J)

        decel_rot = 0.5 * ang_decel * self.t**2

        x = decel_rot*self.ball_r + R*self.ang_v0*self.ball_r*self.t + self.x0
        ang = decel_rot + R*self.ang_v0*self.t + self.ang0
        ang_vel = ang_decel*self.t + R*self.ang_v0

        return round(x), ang, ang_vel

    def is_stillstand(self, ang_vel):
        self.ang_vel_1_2.append((abs(ang_vel)))
        if len(self.ang_vel_1_2) == 2:
            if self.ang_vel_1_2[1] > self.ang_vel_1_2[0]:
                return True
            self.ang_vel_1_2 = []


class CrashHandler:

    def __init__(self, cone_obj):
        self._cone_obj = cone_obj
        self._crash_loc = None
        self._impuls = None
        self.crashed = False

    def record(self, x1, x2, x3, x4):
        if self.crashed:
            if self._crash_loc is None:
                self._crash_loc = x1
            if self._impuls is None:
                # calculated crash_impuls still not realistic
                self._impuls = x2 / self._cone_obj.height

    def reset(self):
        self._crash_loc = None
        self._crash_impuls = None
        self.crashed = False

    @property
    def ball(self):
        return self._ball

    @property
    def crash_loc(self):
        return self._crash_loc

    @property
    def impuls(self):
        return self._impuls
