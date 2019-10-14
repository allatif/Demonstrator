import os
import math as m

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
        self.fps = pg_init.FPS
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
        self.state.update(self.screen)

    def flip_state(self):
        """When a State changes to done necessary startup and cleanup
        functions are called and the current State is changed."""
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(persist)
        self.state.previous = previous

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
        """Object logic for mouse hovering"""
        if obj.inside(mouse):
            obj.mouseover = True
            if hasattr(obj, 'color'):
                obj.color = obj.hov_color
            if hasattr(obj, 'virgin'):
                obj.virgin = False
        else:
            obj.mouseover = False
            if hasattr(obj, 'color'):
                obj.color = obj.obj_color

    def slider_group_logic(self, mouse, slider_obj_list):
        """Slider logic when mouse grabs any thumb of one of the sliders."""
        for slider in slider_obj_list:
            thumb = slider.thumb
            self.hover_object_logic(mouse, thumb)

            if slider.thumb.grabbed:
                slider.slide(mouse)
            slider.update()

    def update(self, surface):
        """Update method for state. Must be overrided in children."""
        pass

    def draw_slider_group(self, surface, slider_group_obj):
        """Draws all sliders as a group with thumb and value label that where
        passed through a list."""
        for slider in slider_group_obj.sliders:
            # Slider Track
            pg.gfxdraw.box(surface, slider.track.rect, slider.track_color)

            # Slider filled Track
            slid_color = slider.act_filled_color
            if not slider.active:
                slid_color = slider.dea_filled_color
            pg.gfxdraw.box(surface, slider.get_slid_rect(), slid_color)

            # Slider Thumb
            thumb_color = slider.act_thumb_color
            if not slider.active:
                thumb_color = slider.dea_thumb_color
            self._draw_aafilled_circle(surface, slider.thumb.c_x,
                                       slider.thumb.c_y,
                                       slider.thumb.r,
                                       thumb_color)

            # Value Label Text
            text_color = slider.act_value_color
            if not slider.active:
                text_color = slider.dea_value_color
            slider.value_label.cache_font('Liberation Sans',
                                          slider.value_label.size,
                                          only_font=True)
            font = slider.value_label.font_cache
            text = font.render(str(slider.value), True, text_color)

            surface.blit(text, slider.value_label.rect)

    def draw_checkbox(self, surface, checkbox_obj):
        """Draws checkbox with text label and cross if checked."""
        rect = checkbox_obj.rect
        width = checkbox_obj.border_width

        # Box
        if checkbox_obj.box_color is None:
            pg.draw.rect(surface, checkbox_obj.border_color, rect, width)
        else:
            pg.draw.rect(surface, checkbox_obj.box_color, rect)
            pg.draw.rect(surface, checkbox_obj.border_color, rect, width)

        # Label Text
        text_color = checkbox_obj.text_color
        if text_color is None:
            text_color = checkbox_obj.border_color

        checkbox_obj.cache_font(checkbox_obj.label.text, 'Liberation Sans',
                                checkbox_obj.height, text_color)
        surface.blit(checkbox_obj.font_cache, checkbox_obj.label.rect)

        if checkbox_obj.checked:
            # Checkbox Cross
            for line in checkbox_obj.gen_cross(margin=5):
                pg.draw.line(surface, checkbox_obj.border_color,
                             *line, checkbox_obj.cross_width)

    def draw_button(self, surface, button_obj):
        """Draws button with text and reflection if activated."""
        pg.gfxdraw.box(surface, button_obj.rect, button_obj.color)

        if button_obj.has_refl:
            # Button Reflection
            if button_obj.virgin:
                signal = self.gen_signal_by_loop(4, 80, forobj='But_Refl')
                button_obj.run(signal)
                self._draw_aafilled_polygon(surface,
                                            button_obj.get_refl_poly(),
                                            button_obj.hov_color)

        # Button Text
        size = button_obj.text_size
        button_obj.cache_font(button_obj.text, 'Liberation Sans', size,
                              button_obj.text_color, center=button_obj.center)
        surface.blit(button_obj.font_cache[0], button_obj.font_cache[1])

    def render_hud(self, length, wide, margin, pos):
        """Returns the rect of hud field"""
        if pos == 'left':
            hud_pos_x = margin
            hud_pos_y = self.height - margin - wide
        elif pos == 'right':
            hud_pos_x = self.width - margin - length
            hud_pos_y = self.height - margin - wide
        rect = (hud_pos_x, hud_pos_y, length, wide)
        return rect

    @staticmethod
    def get_font(name, size):
        """Returns a font only."""
        if name in pg_init.FONTS:
            font = pg_init.FONTS[name]
            return pg.font.Font(font, size)
        return pg.font.SysFont(name, size)

    @staticmethod
    def render_font(text, name, size, color, center=None):
        """Returns the rendered font surface and its rect centered on center,
        if required."""
        font = _State.get_font(name, size)
        text = font.render(text, True, color)
        if center is not None:
            rect = text.get_rect(center=center)
            return text, rect
        return text

    @staticmethod
    def _draw_aafilled_polygon(surface, points, color):
        pg.gfxdraw.aapolygon(surface, points, color)
        pg.gfxdraw.filled_polygon(surface, points, color)

    @staticmethod
    def _draw_aafilled_circle(surface, x, y, r, color):
        pg.gfxdraw.aacircle(surface, x, y, r, color)
        pg.gfxdraw.filled_circle(surface, x, y, r, color)

    @staticmethod
    def deg2rad(deg):
        return deg * (m.pi/180)

    @staticmethod
    def rad2deg(rad):
        return (rad*180) / m.pi


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
