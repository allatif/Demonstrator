import math as m


class Cone:

    def __init__(self, basis_length, basis_center_x, basis_y=500, ratio=1.0):
        self.size = basis_length
        self._start_pos_x = basis_center_x
        self.basis_c_x = basis_center_x
        self.basis_y = basis_y
        self.ratio = ratio

    def update(self):
        self._point_left = self.basis_c_x - (self.size/2), self.basis_y
        self._point_right = self.basis_c_x + (self.size/2), self.basis_y
        self._point_top = self.basis_c_x, self.basis_y - self.size*self.ratio

    def move(self, x1, rate=None):
        if rate is None:
            rate = self.size
        self.basis_c_x = self._start_pos_x + x1*rate

    def get_points(self, point=None):
        if point is None:
            return self._point_left, self._point_right, self._point_top
        elif point == 'left':
            return self._point_left
        elif point == 'right':
            return self._point_right
        elif point == 'top':
            return self._point_top

    def get_coords(self):
        x1, y1 = self._point_left
        x2, y2 = self._point_right
        x3, y3 = self._point_top
        return int(x1), int(y1), int(x2), int(y2), int(x3), int(y3)

    def get_basis_angle(self):
        return m.atan(2*self.ratio)


class Sphere:

    def __init__(self, radius, mass, inertia):
        self.r = radius
        self.mass = mass
        self.J = inertia
        self.touchdown = False

    def update(self, apex_pos, angle):
        polar_angle = 0.5*m.pi - angle
        self._c_x = round(apex_pos[0] + self.r*m.cos(polar_angle))
        self._c_y = round(apex_pos[1] - self.r*m.sin(polar_angle))
        self.touchdown = False

    def fall(self, x, y, ground):
        self._c_x = x
        self._c_y = y
        if self._c_y+self.r >= ground:
            self._c_y = ground - self.r
            self.touchdown = True

    def get_center(self):
        return self._c_x, self._c_y

    def get_equator_line(self, angle):
        rim_x = round(self.r*m.cos(angle))
        rim_y = round(self.r*m.sin(angle))
        point_left = self._c_x - rim_x, self._c_y - rim_y
        point_right = self._c_x + rim_x, self._c_y + rim_y
        return point_left, point_right

    def get_equator_tape(self, angle, width):
        point_left, point_right = self.get_equator_line(angle)
        w_x = round((width//2) * m.sin(-angle))
        w_y = round((width//2) * m.cos(-angle))
        p_top_left = point_left[0] - w_x, point_left[1] - w_y
        p_top_right = point_right[0] - w_x, point_right[1] - w_y
        p_bot_right = point_right[0] + w_x, point_right[1] + w_y
        p_bot_left = point_left[0] + w_x, point_left[1] + w_y
        return p_top_left, p_top_right, p_bot_right, p_bot_left

    def inside(self, mouse):
        return (mouse[0]-self._c_x)**2 + (mouse[1]-self._c_y)**2 < self.r**2


class Ground:

    def __init__(self, pos, length, thickness):
        self._pos = pos
        self.len = length
        self.w = thickness

    def get_line(self):
        start = 0, self._pos
        end = self.len, self._pos
        return start, end

    @property
    def pos(self):
        return self._pos - (self.w//2)
