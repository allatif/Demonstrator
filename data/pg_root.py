import os

import pygame as pg
import pygame.gfxdraw

from . import pg_init


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

    def setup_states(self, state_dict, start_state):
        """Given a dictionary of States and a State to start with,
        builds the self.state_dict."""

        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self):
        """Checks if a state is done or has called for a game quit.
        State is flipped if neccessary and State.update is called."""

        if self.state.quit:
            self.done = True
        elif self.state.done:
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

    def event_handler(self):
        """Process all events and pass them down to current State. The F5 key
        globally turns on/off the display of FPS in the caption"""

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.toggle_show_fps(event.key)

            self.state.get_event(event)

    def mouse_handler(self, mouse):
        """Process mouse position and pass it down to current State"""

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
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
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

        # Temporary variabeles usefull to hold intermediate values
        self._temp_0 = 0
        self._temp_1 = 0
        self._temp_2 = 0

        self._loop_counter = 0

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

    def mouse_logic(self, mouse):
        """Process mouse position that were passed from the main event loop.
        Must be overrided in children."""
        pass

    def hover_object_logic(self, mouse, obj):
        """Object logic for mouse hovering."""

        if obj.inside(mouse):
            obj.mouseover = True
            if hasattr(obj, 'color'):
                obj.color = obj.settings['hover color']
            if hasattr(obj, 'virgin'):
                obj.virgin = False
        else:
            obj.mouseover = False
            if hasattr(obj, 'color'):
                obj.color = obj.settings['button color']

    def instrument_logic(self, mouse, instrument):
        """Instrument logic when mouse grabs thumb of instrument."""

        thumb = instrument.thumb
        self.hover_object_logic(mouse, thumb)

        if thumb.grabbed:
            instrument.slide(mouse)
        instrument.update()

    def update(self, surface):
        """Update method for state. Must be overrided in children."""
        pass

    def draw_slider_group(self, surface, slider_group_obj):
        """Draws all sliders as a group that where passed through
        as slider group object."""

        # Group Header
        header = slider_group_obj.header_label
        if header is not None:
            header.cache_font(slider_group_obj.header_text, 'Liberation Sans',
                              header.size, slider_group_obj.header_color)
            surface.blit(header.font_cache, header.rect)

        for slider in slider_group_obj.sliders:
            self.draw_instrument(surface, slider)

    def draw_instrument(self, surface, instrument):
        """Draws instrument with all its components and name label
        if available."""

        if instrument.name is not None:
            # Instrument Name Label
            name_label = instrument.name_label
            name_label.cache_font(instrument.name, 'Liberation Sans',
                                  name_label.size,
                                  instrument.settings['active value color'])
            surface.blit(name_label.font_cache, name_label.rect)

        if type(instrument).__name__ == 'Slider':
            slider = instrument

            # Slider Track
            pg.gfxdraw.box(surface, slider.track.rect,
                           slider.settings['track color'])

            # Slider Filled Track
            slid_color = slider.settings['active filled color']
            if not slider.active:
                slid_color = slider.settings['deactive filled color']
            pg.gfxdraw.box(surface, slider.get_slid_rect(), slid_color)

            # Slider Thumb
            thumb_color = slider.settings['active thumb color']
            if not slider.active:
                thumb_color = slider.settings['deactive thumb color']
            self._draw_aafilled_circle(surface, slider.thumb.c_x,
                                       slider.thumb.c_y,
                                       slider.thumb.r,
                                       thumb_color)

        if type(instrument).__name__ == 'ControlKnob':
            knob = instrument

            # Control Knob Ring
            self._draw_aafilled_ring(surface, knob.ring.c_x, knob.ring.c_y,
                                     knob.ring.r, knob.ring.w,
                                     knob.settings['track color'])

            # Control Knob Cone Thumb
            thumb = knob.thumb
            thumb_color = knob.settings['active thumb color']
            if not knob.active:
                thumb_color = knob.settings['deactive thumb color']
            pg.gfxdraw.aatrigon(surface, *thumb.get_coords(), thumb_color)
            pg.draw.polygon(surface, thumb_color, thumb.points)

            # Control Knob Pointer
            pointer_color = knob.settings['active pointer color']
            if not knob.active:
                pointer_color = knob.settings['deactive pointer color']
            pygame.draw.aaline(surface, pointer_color,
                               knob.pointer.start, knob.pointer.end)

        # Instrument Value Label
        text_color = instrument.settings['active value color']
        if not instrument.active:
            text_color = instrument.settings['deactive value color']
        instrument.value_label.cache_font('Liberation Sans',
                                          instrument.value_label.size,
                                          only_font=True)
        font = instrument.value_label.font_cache

        text_str = f'{round(instrument.value, 1)}'
        if instrument.unit is not None:
            text_str = f'{round(instrument.value, 1)} {instrument.unit}'

            if type(instrument).__name__ == 'ControlKnob':
                # No space between instrument value and instrument unit
                text_str = f'{round(instrument.value, 1)}{instrument.unit}'

        text = font.render(text_str, True, text_color)

        if type(instrument).__name__ == 'ControlKnob':
            rect = text.get_rect(center=instrument.ring.center)
            surface.blit(text, rect)

        else:
            surface.blit(text, instrument.value_label.rect)

    def draw_label(self, surface, label_obj):
        """Draws label. / # *args = text, font_name, size, color"""
        label_obj.cache_font(label_obj.text, 'Liberation Sans',
                             label_obj.size, label_obj.color)
        text = label_obj.font_cache
        surface.blit(text, label_obj.pos)

    def draw_checkbox_group(self, surface, cbox_group_obj):
        """Draws all checkboxes as a group that where passed through
        as cbox group object."""

        # Group Header
        header = cbox_group_obj.header_label
        if header is not None:
            header.cache_font(cbox_group_obj.header_text, 'Liberation Sans',
                              header.size, cbox_group_obj.header_color)
            surface.blit(header.font_cache, header.rect)

        for cbox in cbox_group_obj.cboxes:
            self.draw_checkbox(surface, cbox)

    def draw_checkbox(self, surface, checkbox_obj):
        """Draws checkbox with text label and cross if checked."""

        rect = checkbox_obj.rect
        width = checkbox_obj.border_width

        # Box / Radio
        border_color = checkbox_obj.settings['border color']
        box_color = checkbox_obj.settings['box color']
        if checkbox_obj.type_ == 'default':
            if box_color is None:
                pg.draw.rect(surface, border_color, rect, width)
            else:
                pg.draw.rect(surface, box_color, rect)
                pg.draw.rect(surface, border_color, rect, width)
        elif checkbox_obj.type_ == 'radio':
            x = rect[0] + checkbox_obj.r
            y = rect[1] + checkbox_obj.r
            r = checkbox_obj.r
            w = width//2
            if box_color is None:
                self._draw_aafilled_ring(surface, x, y, r, w, border_color)
            else:
                self._draw_aafilled_circle(surface, x, y, r, box_color)
                self._draw_aafilled_ring(surface, x, y, r, w, border_color)

        # Label Text
        text_color = checkbox_obj.settings['text color']
        if text_color is None:
            text_color = checkbox_obj.settings['border color']

        checkbox_obj.cache_font(checkbox_obj.label.text, 'Liberation Sans',
                                checkbox_obj.height, text_color)
        surface.blit(checkbox_obj.font_cache, checkbox_obj.label.rect)

        # Checkbox Cross / Radio
        if checkbox_obj.type_ == 'default':
            if checkbox_obj.checked:
                for line in checkbox_obj.gen_cross():
                    pg.draw.line(surface, checkbox_obj.settings['border color'],
                                 *line, checkbox_obj.cross_width)
        elif checkbox_obj.type_ == 'radio':
            if checkbox_obj.checked:
                x, y, r = checkbox_obj.gen_radio()
                self._draw_aafilled_circle(
                    surface, x, y, r,
                    checkbox_obj.settings['border color']
                )

    def draw_list_box(self, surface, list_box_obj):
        """Draws list box by recycling draw_button() method."""

        if list_box_obj.opened:
            list_tuple = tuple(button
                               for button in list_box_obj.options.values())
            self.draw_buttons(surface, *list_tuple)

        self.draw_button(surface, list_box_obj.box_header)
        for layer in list_box_obj.arrow.layerlines:
            for line in layer:
                pg.draw.aaline(surface,
                               list_box_obj.box_header.settings['text color'],
                               line[0], line[1], 0)

    def draw_button(self, surface, button_obj):
        """Draws button with text and reflection if activated."""

        pg.gfxdraw.box(surface, button_obj.rect, button_obj.color)

        if button_obj.settings['reflection']:
            button_obj.settings['refl animation speed'] = 120//self.static_fps
            # Button Reflection
            if button_obj.virgin:
                button_obj.run()
                # Reflection rect for vertical flow
                if button_obj.reflection.rrect_v.rect[3] != 0:
                    pg.draw.rect(surface,
                                 button_obj.settings['reflection color'],
                                 button_obj.reflection.rrect_v.rect)
                # Reflection rect for horizontal flow
                if button_obj.reflection.rrect_h.rect[2] != 0:
                    pg.draw.rect(surface,
                                 button_obj.settings['reflection color'],
                                 button_obj.reflection.rrect_h.rect)

        # Button Text
        size = button_obj.settings['text size']
        button_obj.cache_font(button_obj.text, 'Liberation Sans', size,
                              button_obj.settings['text color'],
                              center=button_obj.center)
        if button_obj.settings['text align center']:
            surface.blit(button_obj.font_cache[0], button_obj.font_cache[1])
        else:
            pos = button_obj.font_cache[1]
            pos[0] = button_obj.pos[0] + button_obj.settings['text margin left']
            surface.blit(button_obj.font_cache[0], pos)

    def draw_buttons(self, surface, *args):
        """Draws buttons by calling draw_button() method."""

        for arg in args:
            self.draw_button(surface, arg)

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
            model_list.append(model_file)
        return model_list

    @staticmethod
    def _draw_aafilled_polygon(surface, points, color):
        pg.gfxdraw.aapolygon(surface, points, color)
        pg.gfxdraw.filled_polygon(surface, points, color)

    @staticmethod
    def _draw_aafilled_circle(surface, x, y, r, color):
        pg.gfxdraw.aacircle(surface, x, y, r, color)
        pg.gfxdraw.filled_circle(surface, x, y, r, color)

    @staticmethod
    def _draw_aafilled_ring(surface, x, y, r, w, color):
        pg.gfxdraw.aacircle(surface, x, y, r-w-1, color)
        pg.gfxdraw.aacircle(surface, x, y, r-w, color)
        pg.gfxdraw.aacircle(surface, x, y, r-1, color)
        pg.gfxdraw.aacircle(surface, x, y, r, color)
        pg.draw.circle(surface, color, (x, y), r, w)

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
