from . label import Label


class Slider:

    _slider_amt = 0
    values = []

    def __init__(self, value, pos_x, pos_y, length, range_, track_color,
                 act_filled_color, act_thumb_color, act_value_color,
                 dea_filled_color=None, dea_thumb_color=None,
                 dea_value_color=None, width=2, gap=20, radius=3, margin=10):
        self.value = value
        self.pos_x = pos_x
        self.pos_y = pos_y + gap*Slider._slider_amt
        self.length = length + 2*radius
        self.width = width
        self.start, self.end = range_

        # Color attrs
        self.track_color = track_color
        self.act_filled_color = act_filled_color
        self.act_thumb_color = act_thumb_color
        self.act_value_color = act_value_color
        self.dea_filled_color = dea_filled_color
        self.dea_thumb_color = dea_thumb_color
        self.dea_value_color = dea_value_color

        # Subclasses
        self.track = Track(self.pos_x, self.pos_y, self.length, self.width)
        self.thumb = Thumb(self.pos_x + radius, self.pos_y, radius)
        self.value_label = Label(self.pos_x + self.length, self.pos_y,
                                 8*self.width, margin, center=True)

        self._min = self.pos_x + radius
        self._max = self.pos_x + self.length - radius

        self._number = Slider._slider_amt
        self.active = True

        self.set()
        Slider._slider_amt += 1
        Slider.values.append(self.value)

    def set(self):
        self.thumb._c_x = self.get_thumb_from_value()

    def set_name_label(self, text, left, margin=0):
        self.name_label = Label(self._pos_x-left, self._pos_y,
                                self._size, margin, text)

    def slide(self, mouse):
        self.thumb._c_x = mouse[0]
        if mouse[0] < self._min:
            self.thumb._c_x = self._min
        if mouse[0] > self._max:
            self.thumb._c_x = self._max

    def update(self):
        pixel_value = self.thumb.c_x - self._min
        ratio = (self.end-self.start) / (self._max-self._min)
        self.value = pixel_value*ratio + self.start
        Slider.values[self.number] = self.value

    def get_thumb_from_value(self):
        ratio = (self.end-self.start) / (self._max-self._min)
        return int(round((self.value-self.start) / ratio + self._min))

    def get_slid_rect(self):
        dyn_length = self.thumb.c_x - self.pos_x
        return self.pos_x, self.pos_y, dyn_length, self.width

    @property
    def number(self):
        return self._number


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
