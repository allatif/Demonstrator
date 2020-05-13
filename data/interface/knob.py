import math as m

from . instrument import Instrument
from . label import Label
from .. components import colors


class ControlKnob(Instrument):

    def __init__(self, value, range_, radius, label_size, color_pack,
                 name=None, margin=10, unit=None):
        Instrument.__init__(self, value, range_, name, color_pack, margin, unit)
        self._r = radius

        # Square inside ring
        self._label_size = label_size
        self._r_i = round((m.sqrt(2)/2) * (self._label_size+self.margin))
        self._width = self._r - self._r_i

        # Add setting keys
        self._settings['active pointer color'] = color_pack['intro']
        self._settings['deactive pointer color'] = colors.DGREY

        # Control Knob screened angle
        self._ang = 0

    def _init_components(self):
        """Need to be called by build method."""

        # Min / max positions and value range to pixel range ratio
        self._min = round(self._ins_x + self._r - m.sin(m.radians(60))*self._r)
        self._max = round(self._ins_x + self._r + m.sin(m.radians(60))*self._r)
        self._ratio = (self._end-self._start) / (self._max-self._min)

        # # Subclasses
        # Initialize Control Knob ring
        self._ring = Ring(self._ins_x+self._r, self._ins_y+self._r,
                          self._r, self._width)

        # Initialize Control Knob cone thumb and Knob Pointer
        self._thumb = ConeThumb(20, 30)
        self._pointer = Pointer()
        self.set()

        # Initialize Control Knob label for value
        self._value_label = Label(self._ring._c_x, self._ring._c_x,
                                  self._label_size, center=True)

        # Initialize Control Knob name label
        if self.name is not None:
            self._name_label = Label(self._pos_x, self._pos_y,
                                     self._label_size, center=True)

    def update(self):
        # Calculation of Thumb's Y position
        rel_distance_to_ring_center = self.ring._c_x - self._thumb._x
        self._ang = m.asin(rel_distance_to_ring_center/self._r)
        self._thumb._y = round(self._ring._c_y+self._ring._r*m.cos(self._ang))

        # Calculation Pointer positions
        self.pointer._start_x, self.pointer._start_y = self._thumb.points[0]
        self.pointer._end_x = round(self.ring._c_x
                                    - m.sin(self._ang)*(self._r_i-1))
        self.pointer._end_y = round(self._ring._c_y
                                    + (self._r_i-1)*m.cos(self._ang))

        Instrument.update(self)

    @property
    def ring(self):
        return self._ring

    @property
    def pointer(self):
        return self._pointer


class Ring:

    def __init__(self, center_x, center_y, radius, width):
        self._c_x = center_x
        self._c_y = center_y
        self._r = radius
        self._w = width

    @property
    def c_x(self):
        return self._c_x

    @property
    def c_y(self):
        return self._c_y

    @property
    def center(self):
        return self._c_x, self._c_y

    @property
    def r(self):
        return self._r

    @property
    def w(self):
        return self._w


class ConeThumb:

    def __init__(self, width, length):
        self._width = width
        self._length = length

        self._x = 0
        self._y = 0
        self._grabbed = False
        self.mouseover = False

    def grab(self):
        self._grabbed = True

    def release(self):
        self._grabbed = False

    def inside(self, point):
        b = (self._width//2)
        in_x = point[0] >= self._x-b and point[0] <= self._x+b
        in_y = point[1] >= self._y and point[1] <= self._y+self._length
        return in_x and in_y

    def get_coords(self):
        x1, y1 = self.points[0]
        x2, y2 = self.points[1]
        x3, y3 = self.points[2]
        return x1, y1, x2, y2, x3, y3

    @property
    def points(self):
        return [(self._x, self._y),
                (self._x-(self._width//2), self._y+self._length),
                (self._x+(self._width//2), self._y+self._length)]

    @property
    def grabbed(self):
        return self._grabbed


class Pointer:

    def __init__(self):
        self._start_x, self._start_y = 0, 0
        self._end_x, self._end_y = 0, 0

    @property
    def start(self):
        return self._start_x, self._start_y

    @property
    def end(self):
        return self._end_x, self._end_y
