import pygame as pg

from . button import Button
from .. components import colors


class ListBox:

    def __init__(self, list_, bg=colors.LGREY, fg=colors.BLACK,
                 hover=colors.LBLUE, action=None, size=(220, 30)):
        self._list = list_
        self._action = action
        self._options = {}
        self._item_height = size[1]

        self._settings = {
            'background': bg,
            'hover': hover,
            'foreground': fg,
            'header': Button._darken_color(bg, 50),
            'text align center': False
        }

        self._box_header = Button('', bg, fg, size=size)
        self._box_header.settings['text margin left'] = 20
        self._arrow = Arrow(12, 6, color=fg)
        for element in list_:
            text = self.compress_text(element)
            self._options[element] = Button(text, bg, fg, size=size)
        self._update_button_settings()

        self.opened = False
        self.selected = None

    def set_pos(self, pos_x, pos_y):
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._box_header.set_pos(pos_x, pos_y)
        self._arrow.buildin(self._box_header.rect)
        for button in self._options.values():
            button.set_pos(pos_x, pos_y)

    def expand(self):
        margin = 2
        for num, button in enumerate(self._options.values()):
            button.set_pos(self._pos_x,
                           self._pos_y + (num+1)*self._item_height + margin)
            button.settings['background'] = self._settings['background']
        self._box_header.settings['background'] = self._settings['header']

        if self.selected is not None:
            self._options[self.selected].settings['background'] \
                = self._settings['header']

        self.opened = True

    def collapse(self):
        self.set_pos(self._pos_x, self._pos_y)
        self._box_header.settings['background'] = self._settings['background']
        self.opened = False

    def pick_up(self):
        if self.selected is not None:
            self._box_header.text = self.compress_text(self.selected)

    def draw(self, surface):
        if self.opened:
            list_tuple = tuple(button for button in self.options.values())
            Button.multidraw(surface, *list_tuple)

        self.box_header.draw(surface)
        for layer in self.arrow.layerlines:
            for line in layer:
                pg.draw.aaline(surface, self.box_header.settings['foreground'],
                               line[0], line[1], 0)

    def _update_button_settings(self):
        head = self._box_header
        for key in self._settings.keys():
            if key in head.settings:
                head.settings[key] = self._settings[key]

        for but in self._options.values():
            for key in self._settings.keys():
                if key in but.settings:
                    but.settings[key] = self._settings[key]

    def _event_logic(self, state, event):

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.opened:
                for key, option in self.options.items():
                    if option.mouseover:
                        self.selected = key
                        if self.action is not None:
                            self.action()
                        self.collapse()
                        self.pick_up()
                    elif not option.mouseover or self.box_header.mouseover:
                        self.collapse()

            elif not self.opened:
                if self.box_header.mouseover:
                    self.expand()

    @staticmethod
    def compress_text(text, maxlen=20, taillen=6):
        ripoff_pos = maxlen - taillen
        isfile = '.' in text[-5:]
        if isfile:
            file, ext = text.split('.')
            extlen = len(ext)+1
            if len(file) > maxlen-extlen:
                return f'{file[:ripoff_pos-extlen]}...{file[-taillen:]}.{ext}'
            return text
        else:
            if len(text) > maxlen:
                return f'{text[:ripoff_pos]}...{text[-taillen:]}'
            return text

    @property
    def list(self):
        return self._list

    @property
    def action(self):
        return self._action

    @property
    def box_header(self):
        return self._box_header

    @property
    def arrow(self):
        return self._arrow

    @property
    def options(self):
        return self._options

    @property
    def choosen_option(self):
        return self._choosen_option

    @property
    def settings(self):
        # self._update_button_settings()
        return self._settings


class Arrow:

    def __init__(self, width, height, color=colors.BLACK, thickness=2):
        self._width = width
        self._height = height
        self._color = color
        self._thickness = thickness
        self._layerlines = []

    def buildin(self, box_rect, margin=10):
        x, y, w, h = box_rect
        c_h = y + h//2
        m = margin
        for i in range(self._thickness):
            # i = layer
            line_1 = (
                # start_pos
                (x + w - m, c_h - self._height//2 + i),
                # end_pos
                (x + w - m - self._width//2, c_h + self._height//2 + i)
            )
            line_2 = (
                # start_pos
                (x + w - m - self._width//2 - 1, c_h + self._height//2 + i),
                # end_pos
                (x + w - m - self._width - 1, c_h - self._height//2 + i)
            )
            lines = [line_1, line_2]
            self._layerlines.append(lines)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def color(self):
        return self._color

    @property
    def thickness(self):
        return self._thickness

    @property
    def layerlines(self):
        return self._layerlines
