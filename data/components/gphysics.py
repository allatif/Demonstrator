import math as m

from .. import pg_init

GRAVITY = 9.81


class gPhysics:

    counter = 0

    def __init__(self, **kwargs):
        self.trigon = kwargs.get('trigon', None)
        self.circle = kwargs.get('circle', None)

        states = kwargs.get('states', None)
        self.loc = states[0]
        self.vel = states[1]
        self.ang = states[2]
        self.ang_vel = states[3]

        self.scale = pg_init.SCALE

        if self.circle is not None and self.trigon is not None:
            # Last position of ball before fall
            self.x0, self.y0 = self.circle.get_center()

            # Slope accelerations when ball rolls down the cone
            self.slope_ang = self.trigon.get_basis_angle()
            self.acc, self.ang_acc = self._calc_accel()

        self.t = 0
        self.fps = 100
        gPhysics.counter = 0

    def update(self):
        gPhysics.counter += 1
        self.t = gPhysics.counter*(1/self.fps)

    def gen_trajectory(self):
        # Not in use, still in beta stage
        vel = 0 if self.collided else self.vel
        x = (vel * self.t * m.cos(self.ang)) * self.scale + self.x0
        y = -(vel * self.t * m.sin(self.ang)
              - (GRAVITY/2) * self.t**2) \
            * self.scale + self.y0
        return round(x), round(y)

    def gen_slope(self):
        real_radius = self.circle.r / self.scale
        # Direction switch depending on angle of dip
        switch = {'left': -1, 'right': 1}
        key = 'left' if self.ang < 0 else 'right'
        distance = (0.5*self.acc*self.t**2
                    + abs(self.ang_vel*real_radius)*self.t)
        x = switch[key]*m.cos(self.slope_ang)*distance*self.scale + self.x0
        y = m.sin(self.slope_ang)*distance*self.scale + self.y0
        return round(x), round(y)

    def gen_slope_rot(self):
        acc_rot = 0.5 * self.ang_acc * self.t**2
        if self.ang_vel < 0:
            self.circle.rt_ang_vel = -acc_rot*self.t + self.ang_vel
            return -acc_rot + self.ang_vel*self.t + self.ang
        else:
            self.circle.rt_ang_vel = acc_rot*self.t + self.ang_vel
            return acc_rot + self.ang_vel*self.t + self.ang

    def keep_rot(self, touchdown_x, touchdown_ang, touchdown_ang_v):
        x0 = touchdown_x
        ang0 = touchdown_ang
        ang_v0 = touchdown_ang_v
        real_radius = self.circle.r / self.scale
        c_friction = 0.1

        if ang0 < 0:
            ang_decel = ((self.circle.mass*GRAVITY*c_friction*real_radius)
                         / self.circle.J)
        else:
            ang_decel = -((self.circle.mass*GRAVITY*c_friction*real_radius)
                          / self.circle.J)

        decel_rot = 0.5 * ang_decel * self.t**2

        ang = decel_rot + self.circle.rt_ang_vel*self.t + ang0
        self.circle.rt_ang_vel = ang_decel * self.t + ang_v0
        x = self.circle.rt_ang_vel * real_radius * self.t * self.scale + x0
        return round(x), ang

    def check_collision(self):
        if self.trigon is not None:
            lef_x, lef_y, rig_x, rig_y, top_x, top_y = self.trigon.get_coords()
            slope_lef = (lef_x - top_x) / (lef_y - top_y)
            slope_rig = -slope_lef

        if self.circle is not None and self.trigon is not None:
            base_y = lef_y
            for y in range(top_y, base_y):
                x_lef = slope_lef*(y-top_y) + top_x
                x_rig = slope_rig*(y-top_y) + top_x
                if (self.circle.inside((x_lef, y))
                        or self.circle.inside((x_rig, y))):
                    return True

                return False

        return

    def _calc_accel(self):
        real_radius = self.circle.r / self.scale
        angular_accel = (
            self.circle.mass * GRAVITY * real_radius * m.sin(self.slope_ang)
        ) / self.circle.J
        accel = angular_accel * real_radius
        return accel, angular_accel

    @classmethod
    def reset_time(cls):
        cls.counter = 0
