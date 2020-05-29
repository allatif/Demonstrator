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
        # prepare self._dict
        self._imports = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        self._dict = {name: [] for name, cl in self._imports}
        del self._dict['InterfaceEngine']
        for _key in [key for key in self._dict.keys() if '_' == key[0]]:
            del self._dict[_key]

        self._initcache = {}
        self._groupables = self._get_groupables()

    def load_objects(self, state):
        """Loads all UI objects that exist in every _State and cache them
        in UI dict. Will be called after every flip state."""

        for cl in state.__dict__.values():
            if type(cl).__name__ in self._dict:
                self._dict[type(cl).__name__].append(cl)
            if type(cl) == list:
                for el in cl:
                    if type(el).__name__ in self._dict:
                        self._dict[type(el).__name__].append(el)
                    else:
                        break

        self._overwrite_groupables(state)

        state._loaded = True

    def clear_dict(self):
        """Clears the UI dict. Will be called after _State is done."""

        for key in self._dict.keys():
            self._dict[key] = []

    def clear_groupables(self):
        """Clears all Groupables class variables. Will be called after
        _State is done."""

        for groupable in self._groupables:
            eval(groupable).list_ = []
            eval(groupable).groups = {}
            eval(groupable).gr_key = 0

    def preset(self, state_dict):
        """Reads out all Groupables that were initialized by every _State
        and cache them in initcache. Initcache will overwrite the UI
        groupables class variables after every state flip."""

        self.clear_groupables()
        for state in state_dict.values():
            state.__init__()
            self._initcache[type(state).__name__] = {}
            for ga in self._groupables:
                self._initcache[type(state).__name__][ga] = eval(ga).groups
            self.clear_groupables()

    def manipulate(self, obj_name, attribute, value, condition=None):
        """Can manipulate UI objects from toplevel by setting
        new attributes."""

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
                if key == 'CheckBox':
                    ui_obj._event_logic(state, event)
                    for group in ui_obj.groups.values():
                        group._event_logic(state, event)
                else:
                    ui_obj._event_logic(state, event)

    def logic(self, mouse):
        """Process all interface mouse logic like hovering."""

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

    def _overwrite_groupables(self, state):
        """Overwrites the class variables of Groupables with initcache
        for every _State seperately. Will be called in load_objects method."""

        statename = type(state).__name__

        def get_childnames(classnames, parentnames):
            childnames = {}
            for parentname in parentnames:
                childnames[parentname] = []
                for cl_name in classnames:
                    if issubclass(eval(cl_name), eval(parentname)):
                        childnames[parentname].append(cl_name)
            return childnames

        childnames = get_childnames(self._dict.keys(),
                                    self._initcache[statename].keys())

        for classname, objects in self._dict.items():
            if not not objects:
                for ga in self._groupables:
                    if classname in childnames[ga]:
                        initgroups = self._initcache[statename][ga]
                        max_gr_key = 0
                        if not not initgroups:
                            max_gr_key = max([key for key in initgroups.keys()])

                        eval(ga).groups = {k+max_gr_key: v
                                           for k, v in eval(ga).groups.items()}
                        eval(ga).groups = {**initgroups, **eval(ga).groups}
                        eval(ga).gr_key += max_gr_key

    def _get_groupables(self):
        """Returns a list of names of groupable UI classes.
        Groupables are UI objects that have a group method that forms up a
        Group object inside the UI class. """

        classes = [cl for _, cl in self._imports if hasattr(cl, 'groups')]

        def reduce(classes):
            childs = {}
            for cls_i in classes:
                for cls_j in classes:
                    if cls_i == cls_j:
                        continue
                    if issubclass(cls_i, cls_j):
                        childs[cls_i] = None
            for child in childs.keys():
                if child in classes:
                    classes.remove(child)

        reduce(classes)
        return [c.__name__ for c in classes]

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

    @property
    def dict(self):
        return self._dict

    @property
    def initcache(self):
        return self._initcache

    @property
    def groupables(self):
        return self._groupables
