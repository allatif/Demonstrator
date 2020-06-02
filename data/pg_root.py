import os

import pygame as pg
import pygame.gfxdraw

from . import pg_init
from . import ui_engine


class PygameApp:
    """PygameApp class for entire project

    Contains the main game loop and the event handler which passes events to
    States as needed. Logic for flipping states is also found here.
    """

    def __init__(self, caption=''):
        self.screen = pg.display.get_surface()
        self.caption = caption
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = pg_init.FPS[1]
        self.show_fps = True

        self.mouse = None
        self.state_dict = {}
        self.state_name = None
        self.state = None

        self.ui = ui_engine.InterfaceEngine()

    def setup_states(self, state_dict, start_state):
        """Given a dictionary of States and a State to start with,
        builds the self.state_dict."""

        self.ui.preset(state_dict)

        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

        self.ui.load_objects(self.state)

    def update(self):
        """Checks if a state is done or has called for a game quit.
        State is flipped if neccessary and State.update is called."""

        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.state._loaded = False
            self.ui.clear_groupables()
            self.ui.clear_dict()
            self.flip_state()

        if "game fps binaries" in self.state.persist:
            fps_bins = self.state.persist["game fps binaries"]
            idx = fps_bins.index(True)
            self.fps = pg_init.FPS[idx]

        self.state.static_fps = int(round(self.fps / 1.1))

        self.state.update(self.screen)

    def flip_state(self):
        """When a State changes to done necessary startup and cleanup
        functions are called and the current State is changed."""

        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.previous = previous
        self.state.startup(persist)

        if not self.state._loaded:
            self.ui.load_objects(self.state)
            self.ui.manipulate('Button', 'static_fps', self.state.static_fps,
                               condition=('settings', '_reflection'))

    def event_handler(self):
        """Process all events and pass them down to current State. The F5 key
        globally turns on/off the display of FPS in the caption"""

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.toggle_show_fps(event.key)

            self.ui.state_events(self.state, event)

            self.state.get_event(event)

    def mouse_handler(self, mouse):
        """Process mouse position and pass it down to current State."""

        self.ui.logic(mouse)
        self.state.mouse_logic(mouse)

    def toggle_show_fps(self, key):
        """Press F5 to turn on/off displaying the framerate in the caption."""

        if key == pg.K_F5:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pg.display.set_caption(self.caption)

    def run(self):
        """Main loop for entire program."""

        while not self.done:
            self.clock.tick(self.fps)
            mouse = pg.mouse.get_pos()
            self.event_handler()
            self.mouse_handler(mouse)
            self.update()
            pg.display.update()
            if self.show_fps:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS [{}]" \
                    .format(self.caption, fps, self.state.static_fps)
                pg.display.set_caption(with_fps)


class _State:
    """This is a prototype class for States

    All states should inherit from it. No direct instances of this class
    should be created. Get_event and update must be overloaded in the
    childclass. Startup and cleanup need to be overloaded when there is data
    that must persist between States.
    """

    def __init__(self):
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.persist = {}

        self.hudfont = pg.font.SysFont('Consolas', 12)
        self.static_fps = None
        self.screenshot = None

        self._loaded = False

        # Temporary variabeles usefull to hold intermediate values
        self._temp_0 = None
        self._temp_1 = None
        self._temp_2 = None

        self._loop_counter = 0

    def get_event(self, event):
        """Processes events that were passed from the main event loop.
        Must be overrided in children."""
        pass

    def startup(self, persistant):
        """Add variables passed in persistant to the proper attributes."""

        self.persist = persistant

    def cleanup(self):
        """Add variables that should persist to the self.persist dictionary.
        Then reset State.done to False."""

        self.done = False
        return self.persist

    def save_screen(self, surface):
        """Saves the screenshot of a State to self.screenshot variable."""

        i_str = pg.image.tostring(surface, 'RGB')
        self.screenshot = pg.image.fromstring(i_str, pg_init.SCREEN_SIZE, 'RGB')

    def mouse_logic(self, mouse):
        """Process mouse position that were passed from the main event loop.
        Must be overrided in children."""
        pass

    def update(self, surface):
        """Update method for state. Must be overrided in children."""
        pass

    def render_hud(self, width, height, margin, pos):
        """Returns the rect of hud field. Rect is always in bottom left or
        bottom right position of the screen."""

        if pos == 'center':
            hud_pos_x = pg_init.SCREEN_SIZE[0]//2 - width//2
            hud_pos_y = margin
        elif pos == 'left':
            hud_pos_x = margin
            hud_pos_y = self.height - margin - height
        elif pos == 'right':
            hud_pos_x = self.width - margin - width
            hud_pos_y = self.height - margin - height
        rect = (hud_pos_x, hud_pos_y, width, height)
        return rect

    def run_loop_counter(self, increment=1):
        """Counts up by a specific increment when called in loop."""

        self._loop_counter += increment

    @staticmethod
    def get_font(name, size):
        """Returns a font only."""

        if name in pg_init.FONTS:
            font = pg_init.FONTS[name]
            return pg.font.Font(font, size)
        return pg.font.SysFont(name, size)

    @staticmethod
    def render_font(text, font_name, size, color, center=None):
        """Returns the rendered font surface and its rect centered on center,
        if required."""

        font = _State.get_font(font_name, size)
        text = font.render(text, True, color)
        if center is not None:
            rect = text.get_rect(center=center)
            return text, rect
        return text

    @staticmethod
    def get_models():
        """Returns a list of all TensorFlow model *.h5 file names."""

        directory = os.path.join('data', 'components', 'rl', 'models')
        model_list = []
        for model_file in os.listdir(directory):
            # Ignore all files that start with underscore
            if model_file[0] is not '_':
                model_list.append(model_file)
        return model_list

    @property
    def _i_(self):
        return self._loop_counter


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


def load_all_fonts(directory, accept=(".ttf", ".otf", ".fon", ".fnt")):
    """Create a dictionary of paths to font files in given directory
    if their extensions are in accept."""

    paths = {}
    for file in os.listdir(directory):
        name, ext = os.path.splitext(file)
        if ext.lower() in accept:
            paths[name] = os.path.join(directory, file)
    return paths
