import os
import pygame as pg
from . import pg_init


class PygameApp:

    def __init__(self, caption=''):
        self.screen = pg.display.get_surface()
        self.caption = caption
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = pg_init.FPS
        self.show_fps = True

        self.mouse = None
        self.state_dict = {}
        self.state_name = None
        self.state = None

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self, mouse):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, mouse)

    def flip_state(self):
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(persist)
        self.state.previous = previous

    def event_handler(self, mouse):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.toggle_show_fps(event.key)

            self.state.get_event(event, mouse)

    def toggle_show_fps(self, key):
        if key == pg.K_F5:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pg.display.set_caption(self.caption)

    def run(self):
        """Main loop for entire program."""
        while not self.done:
            self.clock.tick(self.fps)
            self.mouse = pg.mouse.get_pos()
            self.event_handler(self.mouse)
            self.update(self.mouse)
            pg.display.update()
            if self.show_fps:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
                pg.display.set_caption(with_fps)


class _State:

    def __init__(self):
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.persist = {}

    def get_event(self, event):
        """Processes events that were passed from the main event loop.
        Must be overrided in children."""
        pass

    def startup(self, persistant):
        """Add variables passed in persistant to the proper attributes"""
        self.persist = persistant

    def cleanup(self):
        """Add variables that should persist to the self.persist dictionary.
        Then reset State.done to False."""
        self.done = False
        return self.persist

    def update(self, surface):
        """Update method for state. Must be overrided in children."""
        pass

    def render_font(self, font, msg, color, center):
        """Returns the rendered font surface and its rect centered on center.
        """
        msg = font.render(msg, True, color)
        rect = msg.get_rect(center=center)
        return msg, rect


def load_all_gfx(directory, accept=(".png", ".jpg", ".bmp")):
    """Load all graphics with extensions in the accept argument

    If alpha transparency is found in the image the image will be converted
    using convert_alpha().  If no alpha transparency is detected image will be
    converted using convert() and colorkey will be set to colorkey.
    """

    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
            graphics[name] = img
    return graphics
