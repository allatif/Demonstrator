class CheckBox:

    def __init__(self, size, border_width, border_color, box_color=None):
        self._size = size
        self.border_width = border_width
        self.border_color = border_color
        self.box_color = box_color

        self._pos_x = 0
        self._pos_y = 0
        self.checked = False

    def set_pos(self, pos):
        self._pos_x = pos[0]
        self._pos_y = pos[1]
        self._pos = pos

    def set_label(self, text, margin=2):
        self.label = Label(self._pos_x + self._size,
                           self._pos_y,
                           text, margin)

    def inside(self, point):
        in_x = point[0] >= self._pos_x and point[0] <= self._pos_x+self._size
        in_y = point[1] >= self._pos_y and point[1] <= self._pos_y+self._size
        return in_x and in_y

    def gen_cross(self, margin):
        self.cross_width = self.border_width+1
        m = margin
        point_a1 = self._pos_x + m, self._pos_y + m
        point_a2 = self._pos_x + self._size - m, self._pos_y + self._size - m
        point_b1 = self._pos_x + self._size - m, self._pos_y + m
        point_b2 = self._pos_x + m, self._pos_y + self._size - m
        return [point_a1, point_a2], [point_b1, point_b2]

    @property
    def pos(self):
        return self._pos

    @property
    def rect(self):
        return self._pos_x, self._pos_y, self._size, self._size


class Label:

    def __init__(self, pos_x, pos_y, text, margin):
        self.rect = pos_x + margin, pos_y
        self.text = text
