from . _instrument import _Instrument
from . label import Label
from .. components import colors


class Slider(_Instrument):

    def __init__(self, range_, width, length, color_pack, name=None, margin=10,
                 unit=None, default=None):
        _Instrument.__init__(self, range_, name, color_pack, margin, unit,
                             default)
        self._width = width
        self._length0 = length
        self._thumb_r = round(1.5*self._width)
        self._length = self._length0 + 2*self._thumb_r

        # Add setting keys
        self._settings['active filled color'] = color_pack['intro']
        self._settings['deactive filled color'] = colors.DGREY

        # Label size depends on Track width
        self._label_size = 8*self._width

    def _init_components(self):
        """Need to be called by build method."""

        # Min / max positions and value range to pixel range ratio
        self._min = self._ins_x + self._thumb_r
        self._max = self._ins_x + self._length - self._thumb_r
        self._ratio = (self._end-self._start) / (self._max-self._min)

        # # Subclasses
        # Initialize Slider track
        self._track = Track(self._ins_x, self._ins_y, self._length, self._width)

        # Initialize Slider
        thumb_y_corr = 1 if self._width > 2 else 0
        self._thumb = Thumb(self._min, self._ins_y+thumb_y_corr, self._thumb_r)
        self.set()

        # Initialize Slider label for value
        self._value_label = Label(self._ins_x + self._length + self.margin,
                                  self._ins_y, self._label_size, center=True)

        # Initialize Slider name label
        if self.name is not None:
            self._name_label = Label(self._pos_x, self._pos_y,
                                     self._label_size, center=True)

    def set_thumb_radius(self, radius):
        self._thumb_r = radius
        self._length = self._length0 + 2*self._thumb_r

    def get_slid_rect(self):
        zero_pos = self.get_thumb_from_value(0)
        if self._start >= 0:
            zero_pos = self._ins_x
        dyn_length = self._thumb._x - zero_pos
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
        self._x = c_x
        self._y = c_y
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
        return (mouse[0]-self._x)**2 + (mouse[1]-self._y)**2 < (self.r+2)**2

    @property
    def c_x(self):
        return self._x

    @property
    def c_y(self):
        return self._y

    @property
    def r(self):
        return self._r

    @property
    def grabbed(self):
        return self._grabbed
