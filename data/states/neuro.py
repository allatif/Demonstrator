import pygame as pg

from .. import pg_init, pg_root

from .. components import colors, tools
from .. components.rl import neuronal_network
from .. interface import button, listbox, label


class Neuro(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]

        self.sim_ref_state = (0.5, 0)
        self.sim_init_state = (0, 0, 0, 0.3)
        self.limitations = (0.56, 0.56)
        self.models = self.get_models()

        self.model_box = listbox.ListBox(self.models, hover=colors.TOMATO,
                                         action=self._init_ANN)
        self.model_box.set_pos(100, 10)
        # self.model_box.settings['background'] = colors.DGREY
        self.model_box_label = label.Label(10, 10, 18, "Load Model:")

        self.but_set = button.Button(text='Settings', bg=colors.LBLUE,
                                     fg=colors.WHITE, action='SETTINGS')
        self.but_set.set_pos(self.width-self.but_set.width-15, 10)

        # ANN Object
        self.ann = None

    def _init_ANN(self):
        if self.model_box.selected is not None:
            self.ann = neuronal_network.ANN(self.model_box.selected)

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.next = "GAME"

        if self.previous is not 'SPLASH':
            self.sim_ref_state = self.persist["sim reference state"]
            self.sim_init_state = self.persist["sim initial state"]
            self.limitations = self.persist["limitations"]

    def cleanup(self):
        self.done = False
        self.persist["sim reference state"] = self.sim_ref_state
        self.persist["sim initial state"] = self.sim_init_state
        self.persist["limitations"] = self.limitations
        self.persist["selected model"] = self.model_box.selected
        self.persist["bg_image"] = self.screenshot

        if self.next == 'SPLASH':
            if "result" in self.persist:
                del self.persist["result"]
                self.results = None

        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if self.model_box.selected is not None:
                    self.done = True
            if event.key == pg.K_BACKSPACE:
                self.next = "SPLASH"
                self.done = True

    def update(self, surface):
        if self.but_set.pressed:
            self.save_screen(surface)
        self.draw(surface)

    def draw(self, surface):
        surface.fill(colors.WHITE)
        if self.ann is not None:
            self.draw_ann(surface)
        self.draw_interface(surface)

    def draw_ann(self, surface):
        if not self.ann.built:
            self.ann.build()

            ann_surface = pg.Surface((self.ann.image_rect[2],
                                      self.ann.image_rect[3]))
            ann_surface.fill(colors.WHITE)

            for connection in self.ann.connections:
                pg.draw.aaline(ann_surface, connection.color,
                               connection.start, connection.end)

            for neuron in self.ann.neurons:
                tools.draw_aafilled_circle(ann_surface, *neuron.get_center(),
                                           neuron.r, neuron.color)

            self.ann.save_image(ann_surface)

        if self.ann.image is not None:
            surface.blit(self.ann.image, self.ann.image_rect)

    def draw_interface(self, surface):
        self.model_box_label.draw(surface)
        self.but_set.draw(surface)
        self.model_box.draw(surface)
