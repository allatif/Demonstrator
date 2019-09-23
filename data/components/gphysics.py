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

            # Slope accelerations if ball fall from the cone apex
            self.slope_ang = self.trigon.get_basis_angle()
            self.acc, self.ang_acc = self._calc_accel()

        self.t = 0
        self.fps = 100
        gPhysics.counter = 0

    def update(self):
        gPhysics.counter += 1
        self.t = gPhysics.counter*(1/self.fps)

    def gen_trajectory(self):
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

    def keep_rot(self):
        return self.ang_vel*self.t + self.ang

    def gen_slope_rot(self):
        acc_rot = 0.5*self.ang_acc*self.t**2
        if self.ang_vel < 0:
            return -acc_rot + self.keep_rot()
        else:
            return acc_rot + self.keep_rot()

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
