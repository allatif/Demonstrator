import pygame as pg

from .. import pg_init, pg_root

from .. components import color
from .. interface import button


class Splash(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]
        self.next = "POLEMAP"

        # Initialize buttons
        margin = 50
        button_size = (425, 375)
        pos_y = 175
        text_size = 42

        self.but_csd = button.Button('Control System Design',
                                     obj_color=color.LLGREEN,
                                     hov_color=color.LLLGREEN,
                                     text_color=color.BLACK,
                                     size=button_size)
        self.but_csd.set_pos(margin, pos_y)
        self.but_csd.set_text_size(text_size)

        self.but_rl = button.Button('Reinforcement Learning',
                                    obj_color=color.LRED,
                                    hov_color=color.LLRED,
                                    text_color=color.WHITE,
                                    size=button_size)
        self.but_rl.set_pos(self.width-self.but_rl.width-margin, pos_y)
        self.but_rl.set_text_size(text_size)

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.next = "POLEMAP"

    def cleanup(self):
        self.done = False
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            pass

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.but_csd.mouseover:
                self.next = "POLEMAP"
                self.done = True

            if self.but_rl.mouseover:
                pass

    def mouse_logic(self, mouse):
        self.hover_object_logic(mouse, self.but_csd)
        self.hover_object_logic(mouse, self.but_rl)

    def update(self, surface):
        self.draw(surface)

    def draw(self, surface):
        surface.fill(color.DGREY)
        self.draw_interface(surface)
        self.draw_header(surface, "DEMONSTRATOR")

    def draw_interface(self, surface):
        self.draw_button(surface, self.but_csd)
        self.draw_button(surface, self.but_rl)

    def draw_header(self, surface, text):
        fontname = 'ARCADECLASSIC'
        center = (self.width//2-42, 85)
        msg, rect = self.render_font(text, fontname, 128, color.LRED, center)
        pos_x, pos_y, width, height = rect
        alpha_surface = pg.Surface((width+84, height-10), pg.SRCALPHA)
        alpha_surface.fill(color.TRAN150)
        alpha_surface.blit(msg, (42, -3))
        surface.blit(alpha_surface, (pos_x, pos_y, width, height))
