class Instrument:

    def __init__(self, value, range_, color, act_thumb_color,
                 act_value_color, dea_thumb_color=None, dea_value_color=None,
                 name=None, margin=10, unit=None):
        self._value = value
        self._start, self._end = range_
        self.name = name
        self.margin = margin
        self._unit = unit

        # Color attrs
        self.color = color
        self.act_thumb_color = act_thumb_color
        self.act_value_color = act_value_color
        self.dea_thumb_color = dea_thumb_color
        self.dea_value_color = dea_value_color

        # Instrument position
        self._ins_x = 0
        self._ins_y = 0

        self.active = True

    def _init_components(self):
        """Must be overrided in children."""
        pass

    def build(self, x, y, name_margin=None):
        """Need to be called by build method."""

        if self.name is None:
            self._ins_x = x
            self._ins_y = y
        else:
            push_right = len(self.name) * (self._label_size//2) + self.margin
            if name_margin is not None:
                push_right = name_margin
            self._pos_x = x
            self._pos_y = y
            self._ins_x = x + push_right
            self._ins_y = y
        self._init_components()

    def set(self):
        self._thumb._x = self.get_thumb_from_value()

    def slide(self, mouse):
        self._thumb._x = mouse[0]
        if mouse[0] < self._min:
            self._thumb._x = self._min
        if mouse[0] > self._max:
            self._thumb._x = self._max

    def zeroize(self):
        self._thumb._x = self.get_thumb_from_value(0)

    def update(self):
        pixel_value = self._thumb._x - self._min
        self._value = pixel_value*self._ratio + self._start

    def get_thumb_from_value(self, value=None):
        if value is not None:
            return int(round((value-self._start) / self._ratio + self._min))
        return int(round((self._value-self._start) / self._ratio + self._min))

    @property
    def value(self):
        return self._value

    @property
    def unit(self):
        return self._unit

    @property
    def pos(self):
        if self.name is None:
            return self._ins_x, self._ins_y
        return self._pos_x, self._pos_y

    @property
    def thumb(self):
        return self._thumb

    @property
    def value_label(self):
        return self._value_label

    @property
    def name_label(self):
        return self._name_label
