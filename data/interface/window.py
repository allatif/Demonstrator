from . _box import _Box
from .. import pg_init


class MenuWindow(_Box):

    def __init__(self, header, frame=85, inner_margin=20):
        _Box.__init__(self)
        self._header = header
        self._frame = frame
        self._margin = inner_margin
        self._pos_x = pg_init.SCREEN_RECT[0] + self._frame
        self._pos_y = pg_init.SCREEN_RECT[1] + self._frame
        self._width = pg_init.SCREEN_RECT[2] - self._pos_x - self._frame
        self._height = pg_init.SCREEN_RECT[3] - self._pos_y - self._frame
        self._rect = self._pos_x, self._pos_y, self._width, self._height

        # Content position (used for text or objects inside menu box)
        self._con_pos = self._pos_x + self._margin, self._pos_y + self._margin
        self._con_right = self._pos_x + self._width - self._margin
        self._con_bottom = self._pos_y + self._height - self._margin

    @property
    def header(self):
        return self._header

    @property
    def con_pos(self):
        return self._con_pos

    @property
    def con_right(self):
        return self._con_right

    @property
    def con_bottom(self):
        return self._con_bottom
