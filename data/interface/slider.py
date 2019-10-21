from . instrument import Instrument
from . label import Label


class Slider(Instrument):

    def __init__(self, value, range_, width, length, color,
                 act_filled_color, act_thumb_color, act_value_color,
                 dea_filled_color=None, dea_thumb_color=None,
                 dea_value_color=None, name=None, margin=10, unit=None):
        Instrument.__init__(self, value, range_, color,
                            act_thumb_color, act_value_color,
                            dea_thumb_color, dea_value_color,
                            name, margin, unit)
        self._width = width
        self._length0 = length
        self._thumb_r = round(1.5*self._width)
        self._length = self._length0 + 2*self._thumb_r

        # Color attrs
        self.act_filled_color = act_filled_color
        self.dea_filled_color = dea_filled_color

        self._label_size = 8*self._width

    def _init_components(self):
        """Need to be called by build method."""

        # # Subclasses
        # Initialize Slider track
        self._track = Track(self._ins_x, self._ins_y, self._length, self._width)

        # Initialize Slider thumb with min/max positions
        # and value range to pixel range ratio
        thumb_y_corr = 1 if self._width > 2 else 0
        self._thumb = Thumb(self._ins_x + self._thumb_r,
                            self._ins_y + thumb_y_corr,
                            self._thumb_r)
        self._min = self._ins_x + self._thumb_r
        self._max = self._ins_x + self._length - self._thumb_r
        self._ratio = (self._end-self._start) / (self._max-self._min)
        self.set()

        # Initialize Slider label for value
        self._value_label = Label(self._ins_x + self._length + self.margin,
                                  self._ins_y, self._label_size, center=True)

        # Initialize Slider name label
        if self.name is not None:
            self._name_label = Label(self._pos_x, self._pos_y,
                                     self._label_size, center=True)

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
        self._value = pixel_value*self._ratio + self._start

    def get_thumb_from_value(self, value=None):
        if value is not None:
            return int(round((value-self._start) / self._ratio + self._min))
        return int(round((self._value-self._start) / self._ratio + self._min))

    def get_slid_rect(self):
        zero_pos = self.get_thumb_from_value(0)
        if self._start == 0 or self._end == 0:
            zero_pos = self._ins_x
        dyn_length = self._thumb.c_x - zero_pos
        return zero_pos, self._ins_y, dyn_length, self._width

    @property
    def track(self):
        return self._track


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
