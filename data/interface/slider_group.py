from . label import Label


class SliderGroup:

    def __init__(self, list_of_sliders, header_text=None,
                 header_color=None, header_size=None):
        self._sliders = list_of_sliders
        self.header_text = header_text

        self._header_color = header_color
        if header_color is None:
            self._header_color = self._sliders[0].act_value_color

        self._header_size = header_size
        if header_size is None:
            self._header_size = self._sliders[0].value_label.size

        self._header_label = None

    def arrange(self, pos_x, pos_y, gap=None):
        self._pos_x = pos_x
        self._pos_y = pos_y

        self.gap = 10*self._sliders[0]._width
        if gap is not None:
            self.gap = gap

        if self.header_text is not None:
            self._header_label = Label(self._pos_x, self._pos_y,
                                       self._header_size,
                                       text=self.header_text, center=True)

        for num, slider in enumerate(self._sliders):
            add = 1 if self._header_label is not None else 0
            slider.build(self._pos_x, self._pos_y + self.gap*(num+add))

    def get_values(self):
        return [slider.value for slider in self._sliders]

    @property
    def sliders(self):
        return self._sliders

    @property
    def header_color(self):
        return self._header_color

    @property
    def header_size(self):
        return self._header_size

    @property
    def header_label(self):
        return self._header_label

    @property
    def pos(self):
        return self._pos_x, self._pos_y
