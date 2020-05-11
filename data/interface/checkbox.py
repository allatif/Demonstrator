from . box import Box
from . label import Label


class CheckBox(Box):

    def __init__(self, size, border_width, border_color,
                 box_color=None, text_color=None, type_='default'):
        Box.__init__(self)
        self._size = size
        self._width = size
        self._height = size
        self._border_width = border_width
        self._box_color = box_color
        self._border_color = border_color
        self._text_color = text_color
        self._type_ = type_
        self.checked = False

        self._r = None
        if type == 'radio':
            self._r = self._size // 2

    def set_label(self, text, margin=2):
        self._label = Label(self._pos_x+self._width+margin, self._pos_y,
                            self._size, text=text)

    def gen_cross(self, margin):
        self.cross_width = self._border_width+1
        m = margin
        point_a1 = self._pos_x + m, self._pos_y + m
        point_a2 = self._pos_x + self._size - m, self._pos_y + self._size - m
        point_b1 = self._pos_x + self._size - m, self._pos_y + m
        point_b2 = self._pos_x + m, self._pos_y + self._size - m
        return [point_a1, point_a2], [point_b1, point_b2]

    def gen_radio(self, margin):
        if self._r is not None:
            c_x = self._pos_x + self._r
            c_y = self._pos_y + self._r
            r = self._r - margin
            return c_x, c_y, r
        return 0, 0, 0

    @property
    def border_width(self):
        return self._border_width

    @property
    def box_color(self):
        return self._box_color

    @property
    def border_color(self):
        return self._border_color

    @property
    def text_color(self):
        return self._text_color

    @property
    def label(self):
        return self._label

    @property
    def type_(self):
        return self._type_

    @property
    def r(self):
        return self._r
