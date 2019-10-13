from . box import Box


class Label(Box):

    def __init__(self, pos_x, pos_y, size, margin, text='', center=False):
        Box.__init__(self)
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._rect = self._pos_x + margin, self._pos_y
        self._size = size
        if center:
            self._rect = self._pos_x + margin, self._pos_y - (self._size//2)
        self._height = size
        self._width = None
        self.text = text

    @property
    def size(self):
        return self._size
