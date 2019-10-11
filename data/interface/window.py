from .. import pg_init


class MenuWindow:

    def __init__(self, frame=85, inner_margin=20):
        self.frame = frame
        self.margin = inner_margin
        self._pos_x = pg_init.SCREEN_RECT[0] + self.frame
        self._pos_y = pg_init.SCREEN_RECT[1] + self.frame
        self._width = pg_init.SCREEN_RECT[2] - self._pos_x - self.frame
        self._height = pg_init.SCREEN_RECT[3] - self._pos_y - self.frame
        self._rect = self._pos_x, self._pos_y, self._width, self._height

        # Content position (used for text or objects inside menu box)
        self._con_pos = self._pos_x + self.margin, self._pos_y + self.margin

    @property
    def rect(self):
        return self._rect

    @property
    def con_pos(self):
        return self._con_pos
