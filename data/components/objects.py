import math as m

from .. import pg_init
from .. interface.label import Label

SCALE = pg_init.SCALE


class Cone:

    def __init__(self, basis_length, basis_center_x, basis_y=500, ratio=1.0):
        self.size = basis_length
        self._start_pos_x = basis_center_x
        self._basis_c_x = basis_center_x
        self._basis_y = basis_y
        self.ratio = ratio

        self._real_location = 0
        self._height = self.size*self.ratio

    def update(self, x1):
        self._real_location = x1
        self.move(x1)

    def move(self, x1):
        self._basis_c_x = self._start_pos_x + x1*SCALE
        self._point_left = self._basis_c_x - (self.size/2), self._basis_y
        self._point_right = self._basis_c_x + (self.size/2), self._basis_y
        self._point_top = self._basis_c_x, self._basis_y - self.size*self.ratio

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

    def get_zero_pos(self):
        return self._start_pos_x

    def get_center_x(self):
        return self._basis_c_x

    @property
    def loc(self):
        return self._real_location

    @property
    def height(self):
        return self._height


class Sphere:

    def __init__(self, radius, mass, inertia, zero_pos_x):
        self._r = radius
        self._mass = mass
        self._J = inertia
        self._start_pos_x = zero_pos_x

        self._ang = 0
        self._ang_vel = 0
        self.falling = False
        self.touchdown = False
        self.stopped = False
        self.mouseover = False

    def update(self, apex_pos, angle, angle_vel):
        self._ang = angle
        self._ang_vel = angle_vel

        # Swinging Sphere according to ss variable x3 (angle).
        # Moving Sphere according to cone apex.
        polar_angle = 0.5*m.pi - self._ang
        self._c_x = round(apex_pos[0] + self._r*m.cos(polar_angle))
        self._c_y = round(apex_pos[1] - self._r*m.sin(polar_angle))

    def fall(self, x, y, ang, ang_vel, ground):
        self._c_x = x
        self._c_y = y
        self._ang = ang
        self._ang_vel = ang_vel
        if self._c_y+self._r >= ground:
            self._c_y = ground - self._r
            self.touchdown = True

    def roll(self, x, ang):
        self._c_x = x
        self._ang = ang

    def get_center(self):
        return self._c_x, self._c_y

    def get_equator_line(self):
        rim_x = round(self._r*m.cos(self._ang))
        rim_y = round(self._r*m.sin(self._ang))
        point_left = self._c_x - rim_x, self._c_y - rim_y
        point_right = self._c_x + rim_x, self._c_y + rim_y
        return point_left, point_right

    def get_equator_tape(self, width):
        point_left, point_right = self.get_equator_line()
        w_x = round((width//2) * m.sin(-self._ang))
        w_y = round((width//2) * m.cos(-self._ang))
        p_top_left = point_left[0] - w_x, point_left[1] - w_y
        p_top_right = point_right[0] - w_x, point_right[1] - w_y
        p_bot_right = point_right[0] + w_x, point_right[1] + w_y
        p_bot_left = point_left[0] + w_x, point_left[1] + w_y
        return p_top_left, p_top_right, p_bot_right, p_bot_left

    def inside(self, point):
        return (point[0]-self._c_x)**2 + (point[1]-self._c_y)**2 < self._r**2

    def get_props(self):
        return self.r, self._mass, self._J

    @property
    def r(self):
        return self._r

    @property
    def loc(self):
        return (self.get_center()[0] - self._start_pos_x) / SCALE

    @property
    def ang(self):
        return self._ang

    @property
    def ang_vel(self):
        return self._ang_vel


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


class Ruler:

    def __init__(self, pos, zero, length, marker_color):
        self.pos = pos
        self.zero = zero
        self.len = length
        self.scales = []
        self.num_labels = []
        self.marker = RulerMarker(pg_init.SCREEN_SIZE[0]//2,
                                  self.pos+10, marker_color)

    def set_scales(self, main_scale_len, scale_len, scale_w, subs=5):
        self.scale_w = scale_w
        self._numbers = []
        self._positions = []
        start = (0, 0)
        end = (0, 0)

        for side in range(-1, 2, 2):
            step = side*SCALE

            range_end = 0 if side < 0 else self.len
            pxl_offset = 1

            # Sub-Scales
            for pos_x in range(self.zero, range_end, step//subs):
                start = pos_x-pxl_offset, self.pos+1
                end = pos_x-pxl_offset, self.pos + scale_len
                self.scales.append((start, end))

            # Main-Scales with numbers
            for num, pos_x in enumerate(range(self.zero, range_end, step)):
                start = pos_x-pxl_offset, self.pos+1
                end = pos_x-pxl_offset, self.pos + main_scale_len
                self._numbers.append(side*num)
                self._positions.append(pos_x)
                self.scales.append((start, end))

    def set_labels(self, top, size, margin=0):
        for num, pos_x in self.get_numbers():
            self.num_labels.append(Label(pos_x+margin, self.pos+top,
                                         size, text=str(num)))

    def get_numbers(self):
        return list(zip(self._numbers, self._positions))[1:]


class RulerMarker:

    def __init__(self, zero_x, y, color, value=0, size=(10, 30)):
        self._zero_x = zero_x
        self._x = zero_x
        self._y = y
        self._color = color
        self._value = value
        self._width = size[0]
        self._height = 1*size[1]//3
        self._length = 2*size[1]//3
        self._rec_x = self._x - self._width//2
        self._rec_y = self._y + self._height
        self._ratio = 1 / SCALE
        self._grabbed = False
        self.mouseover = False

    def grab(self):
        self._grabbed = True

    def release(self):
        self._grabbed = False

    def set(self, value):
        self._x = self.get_pos_from_value(value) - 1
        self._rec_x = self._x - self._width//2

    def slide(self, mouse):
        self._x = mouse[0]
        self._rec_x = self._x - self._width//2

    def snap(self, value=20):
        temp = self._x / value
        num_dec = temp % 1
        roundup = True if num_dec >= 0.5 else False
        temp = round(temp)
        correction = -10 if roundup else 10
        self._x = temp*value + correction + 1
        self._rec_x = self._x - self._width//2

    def click(self, binary, value=20):
        push = value if bool(binary) else -value
        self._x += push
        self._rec_x = self._x - self._width//2

    def update(self):
        self._value = round((self._x-self._zero_x) * self._ratio, 1)

    def get_pos_from_value(self, value):
        return int(round((value / self._ratio) + self._zero_x))

    def inside(self, point):
        in_x = point[0] >= self._rec_x and point[0] <= self._rec_x+self._width
        in_y = point[1] >= self._rec_y and point[1] <= self._rec_y+self._length
        return in_x and in_y

    @property
    def grabbed(self):
        return self._grabbed

    @property
    def zero_x(self):
        return self._zero_x

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def color(self):
        return self._color

    @property
    def value(self):
        return self._value

    @property
    def width(self):
        return self._width

    @property
    def length(self):
        return self._length

    @property
    def rec_x(self):
        return self._rec_x

    @property
    def rec_y(self):
        return self._rec_y


class Wall:

    def __init__(self, pos, height, thickness, orientation):
        self._pos = pos
        self._h = height
        self._t = thickness
        self._ori = orientation

        WIDTH, HEIGHT = pg_init.SCREEN_SIZE
        if self._ori == 'left':
            x = int(round(self._pos*SCALE))
            self._rect = (x-self._t, 0, self._t, self._h+1)
        elif self._ori == 'right':
            x = WIDTH - int(round(self._pos*SCALE))
            self._rect = (x, 0, self._t, self._h+1)

    def get_zone(self):
        rect = (self._rect[0], 0, int(round(self._pos*SCALE)), self._h+1)
        if self._ori == 'left':
            rect = rect[0], rect[1], -rect[2], rect[3]
        return rect

    @ property
    def t(self):
        return self._t

    @ property
    def rect(self):
        return self._rect
