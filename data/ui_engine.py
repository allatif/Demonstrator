import sys
import inspect

from . interface.button import Button
from . interface.listbox import ListBox
from . interface.checkbox import CheckBox
from . interface._instrument import _Instrument
from . interface.slider import Slider
from . interface.knob import ControlKnob


class InterfaceEngine:

    def __init__(self):
        imports = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        self._dict = {name: [] for name, cl in imports}
        del self._dict['InterfaceEngine']
        for _key in [key for key in self._dict.keys() if '_' == key[0]]:
            del self._dict[_key]

    def load_objects(self, state):
        for cl in state.__dict__.values():
            if type(cl).__name__ in self._dict:
                self._dict[type(cl).__name__].append(cl)
            if type(cl) == list:
                for el in cl:
                    if type(el).__name__ in self._dict:
                        self._dict[type(el).__name__].append(el)
                    else:
                        break

        state._loaded = True

    def clear_dict(self):
        for key in self._dict.keys():
            self._dict[key] = []

    def manipulate(self, obj_name, attribute, value, condition=None):
        for obj in self._dict[obj_name]:

            if condition is not None:
                if type(condition) == tuple:
                    if getattr(obj, condition[0])[condition[1]]:
                        setattr(obj, attribute, value)
                elif type(condition) == str:
                    if getattr(obj, condition):
                        setattr(obj, attribute, value)

            if condition is None:
                setattr(obj, attribute, value)

            if condition:
                setattr(obj, attribute, value)

    def state_events(self, state, event):
        """Process all interface events."""

        for key in self._dict.keys():
            for ui_obj in self._dict[key]:
                if key == 'Button':
                    ui_obj._event_logic(state, event)

                elif key == 'ListBox':
                    ui_obj._event_logic(state, event)

                elif key == 'CheckBox':
                    ui_obj._event_logic(state, event)
                    for group in ui_obj.groups.values():
                        group._event_logic(state, event)

                elif key == 'Slider':
                    ui_obj._event_logic(state, event)

                elif key == 'ControlKnob':
                    ui_obj._event_logic(state, event)

    def logic(self, mouse):
        """Process all interface mouse logic like hover, grab and release."""

        for button in self._dict['Button']:
            self._hover_logic(mouse, button)

        for listbox in self._dict['ListBox']:
            self._hover_logic(mouse, listbox.box_header)
            for option in listbox.options.values():
                self._hover_logic(mouse, option)

        for checkbox in self._dict['CheckBox']:
            self._hover_logic(mouse, checkbox)

        for instrument in self._dict['Slider'] + self._dict['ControlKnob']:
            if instrument.active:
                self._instrument_logic(mouse, instrument)

    def _hover_logic(self, mouse, obj):
        """Object logic for mouse hovering."""

        if obj.inside(mouse):
            obj.mouseover = True
            if hasattr(obj, 'color'):
                obj.color = obj.settings['hover']
            if hasattr(obj, 'virgin'):
                obj.virgin = False
        else:
            obj.mouseover = False
            if hasattr(obj, 'color'):
                obj.color = obj.settings['background']

    def _instrument_logic(self, mouse, instrument):
        """Instrument logic when mouse grabs thumb of instrument."""

        thumb = instrument.thumb
        self._hover_logic(mouse, thumb)

        if thumb.grabbed:
            instrument.slide(mouse)
        instrument.update()

    @ staticmethod
    def clear_classes():
        _Instrument.list_ = []
        _Instrument.groups = {}
        _Instrument.gr_key = 0
        CheckBox.list_ = []
        CheckBox.groups = {}
        CheckBox.gr_key = 0

    @ property
    def dict(self):
        return self._dict
