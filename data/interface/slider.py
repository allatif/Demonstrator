from . label import Label


class Slider:

    def __init__(self, value, range_, width, length, track_color,
                 act_filled_color, act_thumb_color, act_value_color,
                 dea_filled_color=None, dea_thumb_color=None,
                 dea_value_color=None, name=None, margin=10, unit=None):
        self._value = value
        self._start, self._end = range_
        self._width = width
        self._length0 = length
        self._thumb_r = round(1.5*self._width)
        self._length = self._length0 + 2*self._thumb_r

        # Color attrs
        self.track_color = track_color
        self.act_filled_color = act_filled_color
        self.act_thumb_color = act_thumb_color
        self.act_value_color = act_value_color
        self.dea_filled_color = dea_filled_color
        self.dea_thumb_color = dea_thumb_color
        self.dea_value_color = dea_value_color

        self.name = name
        self.margin = margin
        self._unit = unit

        self._label_size = 8*self._width

        self.active = True

    def _init_components(self):
        """Need to be called by build method."""

        # # Subclasses
        # Initialize Slider track
        self._track = Track(self._sld_x, self._sld_y, self._length, self._width)

        # Initialize Slider thumb with min and max positions
        thumb_y_corr = 1 if self._width > 2 else 0
        self._thumb = Thumb(self._sld_x + self._thumb_r,
                            self._sld_y + thumb_y_corr,
                            self._thumb_r)
        self._min = self._sld_x + self._thumb_r
        self._max = self._sld_x + self._length - self._thumb_r
        self.set()

        # Initialize Slider label for value
        self._value_label = Label(self._sld_x + self._length + self.margin,
                                  self._sld_y, self._label_size, center=True)

        # Initialize Slider name label
        if self.name is not None:
            self._name_label = Label(self._pos_x, self._pos_y,
                                     self._label_size, center=True)

    def build(self, x, y, name_margin=None):
        if self.name is None:
            self._sld_x = x
            self._sld_y = y
        else:
            push_right = len(self.name) * (self._label_size//2) + self.margin
            if name_margin is not None:
                push_right = name_margin
            self._pos_x = x
            self._pos_y = y
            self._sld_x = x + push_right
            self._sld_y = y
        self._init_components()

    def set(self):
        self._thumb._c_x = self.get_thumb_from_value()

    def set_thumb_radius(self, radius):
        self._thumb_r = radius
        self._length = self._length0 + 2*self._thumb_r

    def slide(self, mouse):
        self._thumb._c_x = mouse[0]
        if mouse[0] < self._min:
            self._thumb._c_x = self._min
        if mouse[0] > self._max:
            self._thumb._c_x = self._max

    def zeroize(self):
        self._thumb._c_x = self.get_thumb_from_value(0)

    def update(self):
        pixel_value = self._thumb.c_x - self._min
        ratio = (self._end-self._start) / (self._max-self._min)
        self._value = pixel_value*ratio + self._start

    def get_thumb_from_value(self, value=None):
        ratio = (self._end-self._start) / (self._max-self._min)
        if value is not None:
            return int(round((value-self._start) / ratio + self._min))
        return int(round((self._value-self._start) / ratio + self._min))

    def get_slid_rect(self):
        zero_pos = self.get_thumb_from_value(0)
        if self._start == 0 or self._end == 0:
            zero_pos = self._sld_x
        dyn_length = self._thumb.c_x - zero_pos
        return zero_pos, self._sld_y, dyn_length, self._width

    @property
    def value(self):
        return self._value

    @property
    def pos(self):
        if self.name is None:
            return self._sld_x, self._sld_y
        return self._pos_x, self._pos_y

    @property
    def unit(self):
        return self._unit

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
        if radius == 6:
            self._r = radius-1
        self._r0 = self._r
        self._grabbed = False
        self.mouseover = False

    def grab(self):
        self._r += round(self._r / 3)
        self._grabbed = True

    def release(self):
        self._r = self._r0
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
