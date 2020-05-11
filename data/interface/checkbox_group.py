from . label import Label


class CheckboxGroup:

    def __init__(self, list_of_checkboxes, header_text=None,
                 header_color=None, header_size=None):
        self._cboxes = list_of_checkboxes
        self.header_text = header_text

        self._header_color = header_color
        if header_color is None:
            self._header_color = self._cboxes[0].border_color

        self._header_size = header_size
        if header_size is None:
            self._header_size = self._cboxes[0].label.size

        self._header_label = None

    def arrange(self, pos_x, pos_y, gap=None):
        self._pos_x = pos_x
        self._pos_y = pos_y

        self.gap = 10*self._cboxes[0]._height
        if gap is not None:
            self.gap = gap

        if self.header_text is not None:
            self._header_label = Label(self._pos_x, self._pos_y,
                                       self._header_size,
                                       text=self.header_text, center=True)

        for num, cbox in enumerate(self._cboxes):
            add = 1 if self._header_label is not None else 0
            cbox.set_pos(self._pos_x, self._pos_y + self.gap*(num+add))

    def get_bools(self):
        return [cbox.checked for cbox in self._cboxes]

    @property
    def cboxes(self):
        return self._cboxes

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
