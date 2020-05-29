import pygame as pg

from . _instr_group import _InstrumentGroup
from .. components import colors, tools


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
            self._value = int(round(self._value))

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

    def draw(self, surface):
        if self.name is not None:
            # Instrument Name Label
            name_label = self.name_label
            name_label.cache_font(self.name, 'Liberation Sans',
                                  name_label.size,
                                  self.settings['active value color'])
            surface.blit(name_label.font_cache, name_label.rect)

        if type(self).__name__ == 'Slider':
            slider = self

            # Slider Track
            pg.gfxdraw.box(surface, slider.track.rect,
                           slider.settings['track color'])

            # Slider Filled Track
            slid_color = slider.settings['active filled color']
            if not slider.active:
                slid_color = slider.settings['deactive filled color']
            pg.gfxdraw.box(surface, slider.get_slid_rect(), slid_color)

            # Slider Thumb
            thumb_color = slider.settings['active thumb color']
            if not slider.active:
                thumb_color = slider.settings['deactive thumb color']
            tools.draw_aafilled_circle(surface, slider.thumb.c_x,
                                       slider.thumb.c_y,
                                       slider.thumb.r,
                                       thumb_color)

        if type(self).__name__ == 'ControlKnob':
            knob = self

            # Control Knob Ring
            tools.draw_aafilled_ring(surface, knob.ring.c_x, knob.ring.c_y,
                                     knob.ring.r, knob.ring.w,
                                     knob.settings['track color'])

            # Control Knob Cone Thumb
            thumb = knob.thumb
            thumb_color = knob.settings['active thumb color']
            if not knob.active:
                thumb_color = knob.settings['deactive thumb color']
            pg.gfxdraw.aatrigon(surface, *thumb.get_coords(), thumb_color)
            pg.draw.polygon(surface, thumb_color, thumb.points)

            # Control Knob Pointer
            pointer_color = knob.settings['active pointer color']
            if not knob.active:
                pointer_color = knob.settings['deactive pointer color']
            pg.draw.aaline(surface, pointer_color,
                           knob.pointer.start, knob.pointer.end)

        # Instrument Value Label
        text_color = self.settings['active value color']
        if not self.active:
            text_color = self.settings['deactive value color']
        self.value_label.cache_font('Liberation Sans', self.value_label.size,
                                    only_font=True)
        font = self.value_label.font_cache

        dec = self._settings['decimal places']
        text_str = f'{round(self.value, dec)}'
        if self.unit is not None:
            text_str = f'{round(self.value, dec)} {self.unit}'

            if type(self).__name__ == 'ControlKnob':
                # No space between instrument value and instrument unit
                text_str = f'{round(self.value, dec)}{self.unit}'

        text = font.render(text_str, True, text_color)

        if type(self).__name__ == 'ControlKnob':
            rect = text.get_rect(center=self.ring.center)
            surface.blit(text, rect)
        else:
            surface.blit(text, self.value_label.rect)

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
                if self.haszero and (self._default == self._start):
                    self.zeroize()
                else:
                    self.neutralize()

    @property
    def value(self):
        return self._value

    @property
    def default(self):
        return self._default

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

    @property
    def settings(self):
        return self._settings
