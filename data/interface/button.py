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

    def set_pos(self, pos_x, pos_y):
        self._pos_x = pos_x
        self._pos_y = pos_y

    def init_reflection(self):
        self._refl_pos = 0
        self._refl = Reflection((self._pos_x, self._pos_y),
                                (self._pos_x+10, self._pos_y+self._height), 20)

    def run(self, signal):
        if not self.inside(self._refl.get_points()[2]):
            self._refl_pos = 0
        if signal:
            self._refl_pos += 1
        self._refl.move(self._refl_pos)

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
    def rect(self):
        return self._pos_x, self._pos_y, self._width, self._height

    @property
    def center(self):
        return self._pos_x + (self._width//2), self._pos_y + (self.height//2)

    @property
    def orgcolor(self):
        return self._orgcolor


class Reflection:

    def __init__(self, top_point, bot_point, width):
        self._top = top_point
        self._bot = bot_point
        self._w = width
        self._points = [(self._top[0], self._top[1]),
                        (self._bot[0], self._bot[1]-1),
                        (self._bot[0]+self._w, self._bot[1]-1),
                        (self._top[0]+self._w, self._top[1])]

    def move(self, x):
        self._points = [(self._top[0]+x, self._top[1]),
                        (self._bot[0]+x, self._bot[1]-1),
                        (self._bot[0]+self._w+x, self._bot[1]-1),
                        (self._top[0]+self._w+x, self._top[1])]

    def get_points(self):
        return self._points
