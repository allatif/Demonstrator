import sys

import pygame as pg

from .. import pg_init, pg_root

from .. components import colors
from .. interface.button import Button


class Splash(pg_root._State):

    def __init__(self):
        pg_root._State.__init__(self)
        self.width = pg_init.SCREEN_RECT[2]
        self.height = pg_init.SCREEN_RECT[3]

        self.game_fps_bins = [False, True]
        self.euler_ministeps = 10

        # Initialize splash menu mode buttons
        margin = 50
        button_size = (425, 250)
        pos_y = 175
        text_size = 42

        self.but_csd = Button(text='Control System Design', bg=colors.LLGREEN,
                              fg=colors.BLACK, action='POLEMAP',
                              size=button_size)
        self.but_csd.set_pos(margin, pos_y)
        self.but_csd.settings['text size'] = text_size

        self.but_rl = Button(text='Reinforcement Learning', bg=colors.LRED,
                             fg=colors.WHITE, action='NEURO', size=button_size)
        self.but_rl.set_pos(self.width-self.but_rl.width-margin, pos_y)
        self.but_rl.settings['text size'] = text_size

        # Initialize setup settings button
        self.but_set = Button(text='Main Settings', bg=colors.LBLUE,
                              fg=colors.WHITE, action='MAINSETTINGS',
                              size=(button_size[0], 75))
        self.but_set.set_pos(margin, button_size[1]+pos_y+margin)
        self.but_set.settings['text size'] = text_size - 6

    def startup(self, persistant):
        pg_root._State.startup(self, persistant)
        self.game_fps_bins = self.persist["game fps binaries"]
        self.euler_ministeps = self.persist["euler ministeps"]

    def cleanup(self):
        self.done = False
        self.persist["game fps binaries"] = self.game_fps_bins
        self.persist["euler ministeps"] = self.euler_ministeps
        self.persist["bg_image"] = self.screenshot
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

    def update(self, surface):
        if self.but_set.pressed:
            self.save_screen(surface)
        self.draw(surface)

    def draw(self, surface):
        surface.fill(colors.DGREY)
        self.draw_interface(surface)
        self.draw_header(surface, "DEMONSTRATOR")

    def draw_interface(self, surface):
        self.draw_buttons(surface, self.but_csd, self.but_rl, self.but_set)

    def draw_header(self, surface, text):
        fontname = 'ARCADECLASSIC'
        center = (self.width//2-42, 85)
        msg, rect = self.render_font(text, fontname, 128, colors.TOMATO, center)
        pos_x, pos_y, width, height = rect
        alpha_surface = pg.Surface((width+84, height-10), pg.SRCALPHA)
        alpha_surface.fill(colors.TRAN150)
        alpha_surface.blit(msg, (42, -3))
        surface.blit(alpha_surface, (pos_x, pos_y, width, height))
