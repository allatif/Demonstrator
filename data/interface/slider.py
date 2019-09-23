class Slider:

    _slider_amt = 0

    def __init__(self, value, pos_x, pos_y, length, range_,
                 width=2, margin=20, radius=3, gap=10):
        self.value = value
        self.pos_x = pos_x
        self.pos_y = pos_y + margin*Slider._slider_amt
        self.length = length + 2*radius
        self.width = width
        self.start, self.end = range_

        self.track = Track(self.pos_x, self.pos_y, self.length, self.width)
        self.thumb = Thumb(self.pos_x + radius, self.pos_y, radius)
        self.value_label = Label(self.pos_x + self.length + gap,
                                 self.pos_y,
                                 font_size=16)

        self._min = self.pos_x + radius
        self._max = self.pos_x + self.length - radius

        Slider._slider_amt += 1

    def slide(self, mouse):
        self.thumb.c_x = mouse[0]
        if mouse[0] < self._min:
            self.thumb.c_x = self._min
        if mouse[0] > self._max:
            self.thumb.c_x = self._max

    def update(self):
        pixel_value = self.thumb.c_x - self._min
        ratio = (self.end-self.start) / (self._max-self._min)
        self.value = pixel_value*ratio + self.start

    def get_thumb_from_value(self):
        ratio = (self.end-self.start) / (self._max-self._min)
        return int(round((self.value-self.start) / ratio + self._min))

    def get_slid_rect(self):
        dyn_length = self.thumb.c_x - self.pos_x
        return self.pos_x, self.pos_y, dyn_length, self.width


class Track:

    def __init__(self, pos_x, pos_y, length, width):
        self.rect = pos_x, pos_y, length, width


class Thumb:

    def __init__(self, c_x, c_y, radius):
        self.c_x = c_x
        self.c_y = c_y
        self.r = radius
        self.grabbed = False

    def grab(self):
        self.r += 1
        self.grabbed = True

    def release(self):
        self.r -= 1
        self.grabbed = False

    def mouse_inside(self, mouse):
        return (mouse[0]-self.c_x)**2 + (mouse[1]-self.c_y)**2 < (self.r+2)**2


class Label:

    def __init__(self, pos_x, pos_y, font_size):
        self.size = font_size
        self.rect = pos_x, pos_y - self.size//2
