import pygame as pg

from . _checkbox_group import _CheckboxGroup
from . _box import _Box
from . label import Label
from .. components import tools


class CheckBox(_Box):

    list_ = []
    groups = {}
    gr_key = 0

    def __init__(self, size, border_width, color, checked=False,
                 name=None, type_='default'):
        _Box.__init__(self)
        self._size = size
        self._width = size
        self._height = size
        self._border_width = border_width
        self._type_ = type_
        self.name = name
        self.checked = checked

        self._r = None
        if type_ == 'radio':
            self._r = self._size // 2

        self._settings = {
            'border color': color,
            'box color': None,
            'text color': color
        }

        CheckBox.list_.append(self)

    def set_label(self, text, margin=2):
        self._label = Label(self._pos_x+self._width+margin, self._pos_y,
                            self._size, text=text)

    def gen_cross(self, margin=4):
        self.cross_width = self._border_width+1
        m = margin
        point_a1 = self._pos_x + m, self._pos_y + m
        point_a2 = self._pos_x + self._size - m, self._pos_y + self._size - m
        point_b1 = self._pos_x + self._size - m, self._pos_y + m
        point_b2 = self._pos_x + m, self._pos_y + self._size - m
        return [point_a1, point_a2], [point_b1, point_b2]

    def gen_radio(self, size=0.7):
        if self._r is not None:
            c_x = self._pos_x + self._r
            c_y = self._pos_y + self._r
            r = round(size * (self._r-self._border_width+1))
            return c_x, c_y, r
        return 0, 0, 0

    def group(self, pos=(20, 20), gap=None, header_text=None, header_color=None,
              header_size=None):
        CheckBox.gr_key += 1
        key = CheckBox.gr_key
        CheckBox.groups[key] = _CheckboxGroup(CheckBox.list_,
                                              header_text=header_text,
                                              header_color=header_color,
                                              header_size=header_size)
        CheckBox.groups[key].arrange(*pos, gap=gap)
        CheckBox.list_ = []

    def draw(self, surface):
        rect = self.rect
        width = self.border_width

        # Box / Radio
        border_color = self.settings['border color']
        box_color = self.settings['box color']
        if self.type_ == 'default':
            if box_color is None:
                pg.draw.rect(surface, border_color, rect, width)
            else:
                pg.draw.rect(surface, box_color, rect)
                pg.draw.rect(surface, border_color, rect, width)
        elif self.type_ == 'radio':
            x = rect[0] + self.r
            y = rect[1] + self.r
            r = self.r
            w = width//2
            if box_color is None:
                tools.draw_aafilled_ring(surface, x, y, r, w, border_color)
            else:
                tools.draw_aafilled_circle(surface, x, y, r, box_color)
                tools.draw_aafilled_ring(surface, x, y, r, w, border_color)

        # Label Text
        text_color = self.settings['text color']
        if text_color is None:
            text_color = self.settings['border color']

        self.cache_font(self.label.text, 'Liberation Sans', self.height,
                        text_color)
        surface.blit(self.font_cache, self.label.rect)

        # Checkbox Cross / Radio
        if self.type_ == 'default':
            if self.checked:
                for line in self.gen_cross():
                    pg.draw.line(surface, self.settings['border color'], *line,
                                 self.cross_width)
        elif self.type_ == 'radio':
            if self.checked:
                x, y, r = self.gen_radio()
                tools.draw_aafilled_circle(surface, x, y, r,
                                           self.settings['border color'])

    def _event_logic(self, state, event):

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.mouseover:
                self.checked = not self.checked

    @property
    def border_width(self):
        return self._border_width

    @property
    def label(self):
        return self._label

    @property
    def type_(self):
        return self._type_

    @property
    def r(self):
        return self._r

    @property
    def settings(self):
        return self._settings
