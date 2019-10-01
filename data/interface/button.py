class Button:

    def __init__(self, size, text, color):
        self._width = size[0]
        self._height = size[1]
        self.text = text
        self.color = color

        self._orgcolor = color
        self._pos_x = 0
        self._pos_y = 0
        self.virgin = True

    def set_pos(self, pos):
        self._pos_x = pos[0]
        self._pos_y = pos[1]
        self._pos = pos

    def init_reflection(self):
        self._refl = Reflection(self.pos, 10, self.height)

    def run(self, signal):
        if signal:
            self._refl.move()
        self._refl.flow()

        for pt in range(4):
            if not self.inside((self._refl.get_points()[pt][0]+self._refl._m,
                                self._refl.get_points()[pt][1]+self._refl._m)):
                self._refl.set_fixed_point(pt)

        if not self.inside((self._refl.get_points()[3][0]+self._refl._m,
                            self._refl.get_points()[3][1])):
            self._refl.build_control(task='reset')

    def inside(self, point):
        in_x = point[0] >= self._pos_x and point[0] <= self._pos_x+self._width
        in_y = point[1] >= self._pos_y and point[1] <= self._pos_y+self._height
        return in_x and in_y

    def get_refl_poly(self):
        return self._refl.get_points()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def pos(self):
        return self._pos

    @property
    def rect(self):
        return self._pos_x, self._pos_y, self._width, self._height

    @property
    def center(self):
        return self._pos_x + (self._width//2), self._pos_y + (self.height//2)

    @property
    def orgcolor(self):
        return self._orgcolor


class Reflection:

    def __init__(self, button_pos, deferment, height, width=30):
        self._b_pos = button_pos
        self._d = deferment
        self._h = height
        self._w = width

        # m is the margin between button edge and reflection
        self._m = 2

        # R is the Ratio of height to deferment
        self._R = height / deferment

        # Polygon starts on the top right of button rect
        self._start = [(self._b_pos[0], self._b_pos[1]),
                       (self._b_pos[0], self._b_pos[1]),
                       (self._b_pos[0], self._b_pos[1]),
                       (self._b_pos[0], self._b_pos[1])]
        self._points = self._start

        self._loc = 0
        self._step = 0
        self._steps = [False, False, False]
        self._fixed_points = [None, None, None, None]

    def move(self):
        self._loc += 1

    def flow(self):
        m = self._m
        R = self._R
        x = self._loc
        xs = [x, x, x, x]

        for pt in range(4):
            if self._fixed_points[pt] is not None:
                xs[pt] = self._fixed_points[pt]

        if self._points[1][0] < self._b_pos[0]+self._d:
            # Growing Triangle
            self._points = [(self._b_pos[0], self._b_pos[1]),
                            (self._b_pos[0]+xs[1], self._b_pos[1]),
                            (self._b_pos[0], self._b_pos[1]+xs[2]*R),
                            (self._b_pos[0], self._b_pos[1]+xs[3]*R)]

        elif (self._points[1][0] >= self._b_pos[0]+self._d
              and self._points[1][0] < self._b_pos[0]+self._w):
            # Building Width of Trapezium
            self._unfix_point(2)
            self._unfix_point(3)
            if self._step == 0:
                if not self._steps[self._step]:
                    self.build_control()
                    x = self._loc
                    xs = [x, x, x, x]

            self._points = [(self._b_pos[0], self._b_pos[1]),
                            (self._b_pos[0]+self._d+xs[1], self._b_pos[1]),
                            (self._b_pos[0]+xs[2], self._b_pos[1]+self._h-m),
                            (self._b_pos[0], self._b_pos[1]+self._h-m)]

        elif (self._points[1][0] >= self._b_pos[0]+self._w
              and self._points[1][0] < self._b_pos[0]+self._d+self._w):
            # Building Rhomboid
            if self._step == 1:
                if not self._steps[self._step]:
                    self.build_control()
                    x = self._loc
                    xs = [x, x, x, x]

            self._points = [(self._b_pos[0]+xs[0], self._b_pos[1]),
                            (self._b_pos[0]+self._w+xs[1], self._b_pos[1]),
                            (self._b_pos[0]+self._w-self._d+xs[2],
                                self._b_pos[1]+self._h-m),
                            (self._b_pos[0], self._b_pos[1]+self._h-m),
                            (self._b_pos[0], self._b_pos[1]+xs[0]*R)]

        else:
            # Moving Rhomboid
            if self._step == 2:
                if not self._steps[self._step]:
                    self.build_control()
                    x = self._loc
                    xs = [x, x, x, x]

            self._points = [(self._b_pos[0]+self._d+xs[0], self._b_pos[1]),
                            (self._b_pos[0]+self._d+self._w+xs[1],
                                self._b_pos[1]),
                            (self._b_pos[0]+self._w+xs[2],
                                self._b_pos[1]+self._h-m),
                            (self._b_pos[0]+xs[3], self._b_pos[1]+self._h-m)]

    def set_fixed_point(self, point):
        if self._fixed_points[point] is None:
            self._fixed_points[point] = self._loc

    def _unfix_point(self, point):
        self._fixed_points[point] = None

    def build_control(self, task='build'):
        if task == 'reset':
            self._loc = 0
            self._step = 0
            self._steps = [False, False, False]
            self._points = self._start
            self._fixed_points = [None, None, None, None]
        elif task == 'build':
            self._loc = 0
            self._steps[self._step] = True
            if self._loc == 0:
                self._step += 1

    def get_points(self):
        return self._points
