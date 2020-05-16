import pygame as pg

from .. import pg_init, pg_root

from .. components import colors
from .. interface import button, list_box


MODELLIST = [f'Neuro_Model_{num}' for num in range(10)]


class Neuro(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.next = "GAME"
        self.sim_ref_state = (0.5, 0)
        self.sim_init_state = (0, 0, 0, 0.3)

        self.model_list = list_box.ListBox(MODELLIST, colors.TOMATO)
        self.model_list.set_pos(120, 10)

        self.but_set = button.Button('Settings', colors.LBLUE, colors.WHITE)
        self.but_set.set_pos(self.width-self.but_set.width-15, 10)

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
        self.persist["bg_image"] = self.screenshot_imagestr
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
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

            if self.model_list.opened:
                for list_option in self.model_list.options.values():
                    if list_option.mouseover:
                        self.model_list.selected = list_option.text
                        self.model_list.collapse()
                        self.model_list.pick_up()

            if self.model_list.box_header.mouseover:
                if not self.model_list.opened:
                    self.model_list.expand()
                elif self.model_list.opened:
                    self.model_list.collapse()

    def mouse_logic(self, mouse):
        self.hover_object_logic(mouse, self.but_set)
        self.hover_object_logic(mouse, self.model_list.box_header)
        for list_option in self.model_list.options.values():
            self.hover_object_logic(mouse, list_option)

    def update(self, surface):
        self.screenshot_imagestr = pg.image.tostring(surface, 'RGB')
        self.draw(surface)

    def draw(self, surface):
        surface.fill(colors.WHITE)
        self.draw_interface(surface)

    def draw_interface(self, surface):
        self.draw_button(surface, self.but_set)
        self.draw_list_box(surface, self.model_list)
