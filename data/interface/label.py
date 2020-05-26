from . _box import _Box
from .. components import colors


class Label(_Box):

    def __init__(self, pos_x, pos_y, size, text='',
                 color=colors.BLACK, center=False):
        _Box.__init__(self)
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._rect = self._pos_x, self._pos_y
        self._size = size
        if center:
            self._rect = self._pos_x, self._pos_y - (self._size//2)
        self._height = size
        self._width = None
        self._color = color
        self.text = text

    @property
    def pos(self):
        return self._pos_x, self._pos_y

    @property
    def size(self):
        return self._size

    @property
    def color(self):
        return self._color
