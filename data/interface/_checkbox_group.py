import pygame as pg

from . label import Label


class _CheckboxGroup:

    def __init__(self, list_of_checkboxes, header_text=None,
                 header_color=None, header_size=None):
        self._cboxes = list_of_checkboxes
        self.header_text = header_text

        self._header_color = header_color
        if header_color is None:
            self._header_color = self._cboxes[0].settings['border color']

        self._header_size = header_size
        if header_size is None:
            self._header_size = self._cboxes[0].label.size

        self._header_label = None
        self._selected_num = None

    def arrange(self, pos_x, pos_y, gap=None):
        self._pos_x = pos_x
        self._pos_y = pos_y

        self.gap = self._cboxes[0]._height + self._cboxes[0]._height//2
        if gap is not None:
            self.gap = gap

        if self.header_text is not None:
            self._header_label = Label(self._pos_x, self._pos_y,
                                       self._header_size,
                                       text=self.header_text, center=True)

        for num, cbox in enumerate(self._cboxes):
            add = 1 if self._header_label is not None else 0
            cbox.set_pos(self._pos_x, self._pos_y + self.gap*(num+add))
            cbox.set_label(cbox.name, margin=10)
            if cbox.checked and cbox.type_ == 'radio':
                self.select_checkbox(num)

    def update(self):
        if self._selected_num is not None:
            for num, cbox in enumerate(self._cboxes):
                if num == self._selected_num:
                    cbox.checked = True
                    continue
                cbox.checked = False

    def get_bools(self):
        return [cbox.checked for cbox in self._cboxes]

    def select_checkbox(self, num):
        self._selected_num = num

    def _event_logic(self, state, event):

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for num, cbox in enumerate(self._cboxes):
                if cbox.mouseover:
                    self.select_checkbox(num)
                    self.update()
                    break

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
