import pygame as pg

from .. import pg_init, pg_root

from .. components import colors
from .. components.rl import neuronal_network
from .. interface import button, list_box, label


class Neuro(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]

        self.sim_ref_state = (0.5, 0)
        self.sim_init_state = (0, 0, 0, 0.3)
        self.models = self.get_models()

        self.model_box = list_box.ListBox(self.models, colors.TOMATO)
        self.model_box.set_pos(100, 10)
        self.model_box_label = label.Label(10, 10, 18, "Load Model:")

        self.but_set = button.Button('Settings', colors.LBLUE, colors.WHITE)
        self.but_set.set_pos(self.width-self.but_set.width-15, 10)

        # ANN Object
        self.ann = None

    def _init_ANN(self, model_name):
        self.ann = neuronal_network.ANN(model_name)
        self.ann.build()

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.next = "GAME"

        if self.previous is not 'SPLASH':
            self.sim_ref_state = self.persist["sim reference state"]
            self.sim_init_state = self.persist["sim initial state"]

    def cleanup(self):
        self.done = False
        self.persist["sim reference state"] = self.sim_ref_state
        self.persist["sim initial state"] = self.sim_init_state
        self.persist["selected model"] = self.model_box.selected
        self.persist["bg_image"] = self.screenshot_imagestr
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if self.model_box.selected is not None:
                    self.done = True
            if event.key == pg.K_BACKSPACE:
                self.next = "SPLASH"
                self.done = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            pass

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.but_set.mouseover:
                self.next = "SETTINGS"
                self.done = True

            if self.model_box.opened:
                for key, option in self.model_box.options.items():
                    if option.mouseover:
                        self.model_box.selected = key
                        self._init_ANN(model_name=key)
                        self.model_box.collapse()
                        self.model_box.pick_up()
                    elif (not option.mouseover
                            or self.model_box.box_header.mouseover):
                        self.model_box.collapse()
            elif not self.model_box.opened:
                if self.model_box.box_header.mouseover:
                    self.model_box.expand()

    def mouse_logic(self, mouse):
        self.hover_object_logic(mouse, self.but_set)
        self.hover_object_logic(mouse, self.model_box.box_header)
        for option in self.model_box.options.values():
            self.hover_object_logic(mouse, option)

    def update(self, surface):
        self.screenshot_imagestr = pg.image.tostring(surface, 'RGB')
        self.draw(surface)

    def draw(self, surface):
        surface.fill(colors.WHITE)
        self.draw_ann(surface)
        self.draw_interface(surface)

    def draw_ann(self, surface):
        if self.ann is not None:
            for connection in self.ann.connections:
                pg.draw.aaline(surface, connection.color,
                               connection.start, connection.end)

            for neuron in self.ann.neurons:
                self._draw_aafilled_circle(surface, *neuron.get_center(),
                                           neuron.r, neuron.color)

    def draw_interface(self, surface):
        self.draw_label(surface, self.model_box_label)
        self.draw_button(surface, self.but_set)
        self.draw_list_box(surface, self.model_box)
