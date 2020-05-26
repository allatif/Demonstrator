import pygame as pg

from . _instr_group import _InstrumentGroup
from .. components import colors


class _Instrument:

    list_ = []
    groups = {}
    gr_key = 0

    def __init__(self, range_, name, color_pack, margin, unit, default):
        self._value = 0
        self._start, self._end = range_
        self.name = name
        self.margin = margin
        self._unit = unit
        if default is None:
            self._default = self._start
        else:
            self._default = default

        # Instrument position
        self._ins_x = 0
        self._ins_y = 0

        self.haszero = self._check_zero()
        self.active = True

        self._settings = {
            'track color': colors.GREY,
            'active thumb color': color_pack['contrast'],
            'active value color': color_pack['contrast'],
            'deactive thumb color': colors.BLACK,
            'deactive value color': colors.LGREY,
            'integer': False,
            'decimal places': 1
        }

        _Instrument.list_.append(self)

    def _init_components(self):
        """Must be overrided in children."""
        pass

    def build(self, x, y, name_margin=None):
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

    def set(self, value=None):
        self._thumb._x = self.get_thumb_from_value(value)

    def slide(self, mouse):
        self._thumb._x = mouse[0]
        if mouse[0] < self._min:
            self._thumb._x = self._min
        if mouse[0] > self._max:
            self._thumb._x = self._max

    def zeroize(self):
        self._thumb._x = self.get_thumb_from_value(0)

    def neutralize(self):
        self._thumb._x = self.get_thumb_from_value(self._default)

    def update(self):
        pixel_value = self._thumb._x - self._min
        dec = self._settings['decimal places']
        self._value = round(pixel_value*self._ratio + self._start, dec)
        if self._settings['integer']:
            self._value = int(self._value)

    def get_thumb_from_value(self, value=None):
        if value is not None:
            return int(round((value-self._start) / self._ratio + self._min))
        return int(round((self._value-self._start) / self._ratio + self._min))

    def group(self, pos=(20, 20), gap=None, header_text=None, header_color=None,
              header_size=None):
        _Instrument.gr_key += 1
        key = _Instrument.gr_key
        _Instrument.groups[key] = _InstrumentGroup(_Instrument.list_,
                                                   header_text=header_text,
                                                   header_color=header_color,
                                                   header_size=header_size)
        _Instrument.groups[key].arrange(*pos, gap=gap)
        _Instrument.list_ = []

    def _check_zero(self):
        start = int(round(self._start))
        end = int(round(self._end+1))
        if end < 0:
            start, end = end, start
        return 0 in [i for i in range(start, end+1, 1)]

    def _event_logic(self, state, event):

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.thumb.mouseover:
                self.thumb.grab()

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.thumb.grabbed:
                self.thumb.release()

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            if self.thumb.mouseover:
                if self.haszero:
                    self.zeroize()
                else:
                    self.neutralize()

    @ property
    def value(self):
        return self._value

    @ property
    def default(self):
        return self._default

    @ property
    def unit(self):
        return self._unit

    @ property
    def pos(self):
        if self.name is None:
            return self._ins_x, self._ins_y
        return self._pos_x, self._pos_y

    @ property
    def thumb(self):
        return self._thumb

    @ property
    def value_label(self):
        return self._value_label

    @ property
    def name_label(self):
        return self._name_label

    @ property
    def settings(self):
        return self._settings
