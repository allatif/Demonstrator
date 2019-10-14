from . label import Label


class Slider:

    def __init__(self, value, width, length, range_, track_color,
                 act_filled_color, act_thumb_color, act_value_color,
                 dea_filled_color=None, dea_thumb_color=None,
                 dea_value_color=None, pos_x=0, pos_y=0, margin=10):
        self._value = value
        self._width = width
        self.thumb_r = round(1.5*self._width)
        self.length = length + 2*self.thumb_r
        self._start, self._end = range_

        # Color attrs
        self.track_color = track_color
        self.act_filled_color = act_filled_color
        self.act_thumb_color = act_thumb_color
        self.act_value_color = act_value_color
        self.dea_filled_color = dea_filled_color
        self.dea_thumb_color = dea_thumb_color
        self.dea_value_color = dea_value_color

        self._pos_x = pos_x
        self._pos_y = pos_y
        self.margin = margin

        self._init_components()

        self.active = True

    def _init_components(self):
        # Subclasses
        self._track = Track(self._pos_x, self._pos_y, self.length, self._width)

        thumb_y_corr = 1 if self._width > 2 else 0
        self._thumb = Thumb(self._pos_x + self.thumb_r,
                            self._pos_y+thumb_y_corr,
                            self.thumb_r)

        self._value_label = Label(self._pos_x + self.length, self._pos_y,
                                  8*self._width, self.margin, center=True)

        self._min = self._pos_x + self.thumb_r
        self._max = self._pos_x + self.length - self.thumb_r

        self.set()

    def set(self):
        self._thumb._c_x = self.get_thumb_from_value()

    def set_pos(self, x, y):
        self._pos_x = x
        self._pos_y = y

    def set_name_label(self, text, left, margin=0):
        self._name_label = Label(self._pos_x-left, self._pos_y,
                                 self._size, margin, text)

    def slide(self, mouse):
        self._thumb._c_x = mouse[0]
        if mouse[0] < self._min:
            self._thumb._c_x = self._min
        if mouse[0] > self._max:
            self._thumb._c_x = self._max

    def update(self):
        pixel_value = self._thumb.c_x - self._min
        ratio = (self._end-self._start) / (self._max-self._min)
        self._value = pixel_value*ratio + self._start

    def get_thumb_from_value(self):
        ratio = (self._end-self._start) / (self._max-self._min)
        return int(round((self._value-self._start) / ratio + self._min))

    def get_slid_rect(self):
        dyn_length = self._thumb.c_x - self._pos_x
        return self._pos_x, self._pos_y, dyn_length, self._width

    @property
    def number(self):
        return self._number

    @property
    def value(self):
        return self._value

    @property
    def width(self):
        return self._width

    @property
    def pos(self):
        return self._pos_x, self._pos_y

    @property
    def track(self):
        return self._track

    @property
    def thumb(self):
        return self._thumb

    @property
    def value_label(self):
        return self._value_label

    @property
    def name_label(self):
        return self._name_label


class Track:

    def __init__(self, pos_x, pos_y, length, width):
        self._rect = pos_x, pos_y, length, width

    @property
    def rect(self):
        return self._rect


class Thumb:

    def __init__(self, c_x, c_y, radius):
        self._c_x = c_x
        self._c_y = c_y
        self._r = radius
        self._grabbed = False
        self.mouseover = False

    def grab(self):
        self._r += round(self._r / 3)
        self._grabbed = True

    def release(self):
        self._r -= round(self._r / 3)
        self._grabbed = False

    def inside(self, mouse):
        return (mouse[0]-self.c_x)**2 + (mouse[1]-self.c_y)**2 < (self.r+2)**2

    @property
    def c_x(self):
        return self._c_x

    @property
    def c_y(self):
        return self._c_y

    @property
    def r(self):
        return self._r

    @property
    def grabbed(self):
        return self._grabbed
