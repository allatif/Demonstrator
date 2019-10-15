from . box import Box
from . label import Label


class CheckBox(Box):

    def __init__(self, size, border_width, border_color,
                 box_color=None, text_color=None):
        Box.__init__(self)
        self._size = size
        self._width = size
        self._height = size
        self._border_width = border_width
        self._box_color = box_color
        self._border_color = border_color
        self._text_color = text_color
        self.checked = False

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
