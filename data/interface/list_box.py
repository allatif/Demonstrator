from . button import Button
from .. components import colors


class ListBox:

    def __init__(self, list_, option_color, box_color=colors.LGREY,
                 text_color=colors.BLACK, size=(160, 30)):
        self._list = list_
        self._options = {}
        self._item_height = size[1]

        self._settings = {
            'box color': box_color,
            'text color': text_color,
            'option color': option_color
        }

        self._box_header = Button('', box_color, text_color, size)
        for element_name in list_:
            self._options[element_name] = Button(element_name, box_color,
                                                 text_color, size)
        self._update_button_settings()

        self.opened = False
        self.selected = None

    def set_pos(self, pos_x, pos_y):
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._box_header.set_pos(pos_x, pos_y)
        for button in self._options.values():
            button.set_pos(pos_x, pos_y)

    def expand(self):
        margin = self._item_height
        for num, button in enumerate(self._options.values()):
            button.set_pos(self._pos_x, self._pos_y + (num+1)*margin)
        self.opened = True

    def collapse(self):
        self.set_pos(self._pos_x, self._pos_y)
        self.opened = False

    def pick_up(self):
        if self.selected is not None:
            self._box_header.text = self.selected

    def _update_button_settings(self):
        self._box_header.settings['button color'] = self._settings['box color']
        self._box_header.settings['hover color'] = self._settings['option color']
        self._box_header.settings['text color'] = self._settings['text color']
        for button in self._options.values():
            button.settings['button color'] = self._settings['box color']
            button.settings['hover color'] = self._settings['option color']
            button.settings['text color'] = self._settings['text color']

    @property
    def list(self):
        return self._list

    @property
    def box_header(self):
        return self._box_header

    @property
    def options(self):
        return self._options

    @property
    def settings(self):
        self._update_button_settings()
        return self._settings
