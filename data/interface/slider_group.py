class SliderGroup:

    def __init__(self, list_of_sliders):
        self._sliders = list_of_sliders

    def arrange(self, pos_x, pos_y, gap=None):
        self._pos_x = pos_x
        self._pos_y = pos_y

        if gap is None:
            self.gap = 10*self._sliders[0].width
        else:
            self.gap = gap

        for num, slider in enumerate(self._sliders):
            slider.set_pos(self._pos_x, self._pos_y + self.gap*num)
            slider._init_components()

    def get_values(self):
        return [slider.value for slider in self._sliders]

    @property
    def sliders(self):
        return self._sliders

    @property
    def slider_amt(self):
        return self._slider_amt

    @property
    def pos(self):
        return self._pos_x, self._pos_y
