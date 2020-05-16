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
            'text align center': False,
            'option color': option_color,
            'header open color': Button._darken_color(box_color)}

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
        margin = self._item_height+1
        for num, button in enumerate(self._options.values()):
            button.set_pos(self._pos_x, self._pos_y + (num+1)*margin)
        self._box_header.settings['button color'] \
            = self._settings['header open color']
        self.opened = True

    def collapse(self):
        self.set_pos(self._pos_x, self._pos_y)
        self._box_header.settings['button color'] = self._settings['box color']
        self.opened = False

    def pick_up(self):
        if self.selected is not None:
            self._box_header.text = self.selected

    def _update_button_settings(self):
        head = self._box_header
        head.settings['button color'] = self._settings['box color']
        head.settings['hover color'] = self._settings['option color']
        head.settings['text color'] = self._settings['text color']
        head.settings['text align center'] = self._settings['text align center']
        for but in self._options.values():
            but.settings['button color'] = self._settings['box color']
            but.settings['hover color'] = self._settings['option color']
            but.settings['text color'] = self._settings['text color']
            but.settings['text align center'] \
                = self._settings['text align center']

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
