class Box:

    def __init__(self):
        self._pos_x = 0
        self._pos_y = 0
        self.mouseover = False

    def set_pos(self, pos_x, pos_y):
        self._pos_x = pos_x
        self._pos_y = pos_y

    def inside(self, point):
        in_x = point[0] >= self._pos_x and point[0] <= self._pos_x+self._width
        in_y = point[1] >= self._pos_y and point[1] <= self._pos_y+self._height
        return in_x and in_y

    @property
    def pos(self):
        return self._pos_x, self._pos_y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def rect(self):
        return self._pos_x, self._pos_y, self._width, self._height
