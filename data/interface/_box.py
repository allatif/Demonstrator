from .. import pg_root


class _Box:

    def __init__(self):
        self._pos_x = 0
        self._pos_y = 0
        self.mouseover = False
        self.font_cache = None

    def set_pos(self, pos_x, pos_y):
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._rect = self._pos_x, self._pos_y, self._width, self._height

    def inside(self, point):
        in_x = point[0] >= self._pos_x and point[0] < self._pos_x+self._width
        in_y = point[1] >= self._pos_y and point[1] < self._pos_y+self._height
        return in_x and in_y

    def cache_font(self, *args, center=None, only_font=False):
        # *args|get_font = font_name, size
        # *args|render_font = text, font_name, size, color
        if self.font_cache is None:
            if only_font:
                self.font_cache = pg_root._State.get_font(args[0], args[1])
            else:
                self.font_cache = pg_root._State.render_font(args[0], args[1],
                                                             args[2], args[3],
                                                             center)

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
        return self._rect
