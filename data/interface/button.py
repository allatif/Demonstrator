import pygame as pg

from . _box import _Box
from .. components import colors


class Button(_Box):

    def __init__(self, text='', fg=colors.BLACK, bg=colors.WHITE, action=None,
                 done=False, size=(90, 30)):
        _Box.__init__(self)
        self._text = text
        self._action = action
        self._done = done
        self._width = size[0]
        self._height = size[1]

        self._settings = {
            'background': bg,
            'hover': self._lighten_color(bg),
            'foreground': fg,
            'text size': round(0.6*self._height),
            'text align center': True,
            'text margin left': 10,
            '_reflection': False,
            'reflection color': self._lighten_color(bg, 2),
            'refl animation speed': 1
        }

        self.color = self._settings['background']

        self.pressed = False
        self.virgin = True

    def activate_reflection(self):
        self._settings['_reflection'] = True
        self._refl = Reflection(self.rect)

    def run(self):
        self._refl.flow(self._settings['refl animation speed'])

    def draw(self, surface):
        pg.gfxdraw.box(surface, self.rect, self.color)

        if self.settings['_reflection']:
            self.settings['refl animation speed'] = 120//self.static_fps
            # Button Reflection
            if self.virgin:
                self.run()
                # Reflection rect for vertical flow
                if self.reflection.rrect_v.rect[3] != 0:
                    pg.draw.rect(surface, self.settings['reflection color'],
                                 self.reflection.rrect_v.rect)
                # Reflection rect for horizontal flow
                if self.reflection.rrect_h.rect[2] != 0:
                    pg.draw.rect(surface, self.settings['reflection color'],
                                 self.reflection.rrect_h.rect)

        # Button Text
        size = self.settings['text size']
        self.cache_font(self.text, 'Liberation Sans', size,
                        self.settings['foreground'], center=self.center)
        if self.settings['text align center']:
            surface.blit(self.font_cache[0], self.font_cache[1])
        else:
            pos = self.font_cache[1]
            pos[0] = self.pos[0] + self.settings['text margin left']
            surface.blit(self.font_cache[0], pos)

    def _event_logic(self, state, event):

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.mouseover:
                self.pressed = True

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.mouseover and self.pressed:
                self.pressed = False
                if type(self.action) == str:
                    state.next = self.action
                    state.done = True
                else:
                    self.action()
                    state.done = self.done

    @staticmethod
    def _lighten_color(color, step=1):
        step = 3 if step >= 3 else step
        extra = 0
        new_color = [0, 0, 0]
        prime = color.index(max(color))
        for idx, component in enumerate(color):
            if idx == prime:
                new_color[idx] = component + 25
                if new_color[idx] > 255:
                    new_color[idx] = 255
            elif component == 0:
                extra = 25
                new_color[idx] = 42
            else:
                backlash = 255 - component
                gamma = step * 0.165
                new_color[idx] = component + int(round(backlash*gamma)) + extra

        return tuple(new_color)

    @classmethod
    def multidraw(cls, surface, *args):
        for arg in args:
            arg.draw(surface)

    @staticmethod
    def _darken_color(color, value=30):
        new_color = [0, 0, 0]
        for idx, component in enumerate(color):
            new_color[idx] = component - value
            if new_color[idx] < 0:
                new_color[idx] = 0

        return tuple(new_color)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self.font_cache = None
        self._text = new_text

    @property
    def action(self):
        return self._action

    @property
    def done(self):
        return self._done

    @property
    def center(self):
        return self._pos_x + (self._width//2), self._pos_y + (self.height//2)

    @property
    def reflection(self):
        return self._refl

    @property
    def settings(self):
        return self._settings


class Reflection:

    def __init__(self, button_rect, width=3):
        self._b_rect = button_rect
        self._w = width
        self._start_rect_v = (
            # x, y, width, height
            self._b_rect[0],
            self._b_rect[1],
            self._w,
            0
        )
        self._start_rect_h = (
            # x, y, width, height
            self._b_rect[0],
            self._b_rect[1] + self._b_rect[3] - self._w,
            0,
            self._w
        )

        self._but_w_h_ratio = int(round(self._b_rect[2]/self._b_rect[3]))

        self._rrect_v = ReflecRect(self._start_rect_v)
        self._rrect_h = ReflecRect(self._start_rect_h)

        self._pause_counter = 0
        self._pause = False

    def flow(self, speed):
        ver_speed = speed
        hor_speed = self._but_w_h_ratio * speed
        if not self._pause:
            if self._rrect_v.rect[1]+self._rrect_v.rect[3] \
                    < self._b_rect[1]+self._b_rect[3]:
                self._rrect_v.stretch_rect(ver_speed, axis=0)
            else:
                self._rrect_v.compress_rect(ver_speed, axis=0)
                if self._rrect_h.rect[0]+self._rrect_h.rect[2] \
                        < self._b_rect[0]+self._b_rect[2]:
                    self._rrect_h.stretch_rect(hor_speed, axis=1)
                else:
                    self._rrect_h.compress_rect(hor_speed, axis=1)
                    if self._rrect_h.rect[2] <= 0:
                        self._pause = True
        elif self._pause:
            self.hold(500//speed)

    def hold(self, time):
        frames = time // 10
        self._pause_counter += 1
        if self._pause_counter >= frames:
            self._pause = False
            self._pause_counter = 0
            self.reset()

    def reset(self):
        self._rrect_v = ReflecRect(self._start_rect_v)
        self._rrect_h = ReflecRect(self._start_rect_h)

    @property
    def rrect_v(self):
        return self._rrect_v

    @property
    def rrect_h(self):
        return self._rrect_h


class ReflecRect:

    def __init__(self, rect):
        self._rect = rect

    def stretch_rect(self, speed, axis=1):
        self._rect_snake(1, speed, axis)

    def compress_rect(self, speed, axis=1):
        self._rect_snake(-1, speed, axis)

    def _rect_snake(self, mode, speed, axis):
        if axis == 0:
            # y direction
            follow_x = 0
            grow_x = 0
            if mode == 1:
                follow_y = 0
                grow_y = speed
            elif mode == -1:
                follow_y = speed
                grow_y = 0
        elif axis == 1:
            # x direction
            follow_y = 0
            grow_y = 0
            if mode == 1:
                follow_x = 0
                grow_x = speed
            elif mode == -1:
                follow_x = speed
                grow_x = 0

        self._rect = (
            # x, y, width, height
            self._rect[0] + follow_x,
            self._rect[1] + follow_y,
            self._rect[2] + grow_x - follow_x,
            self._rect[3] + grow_y - follow_y
        )

        if self._rect[2] < 0:
            self._rect = (self._rect[0], self._rect[1], 0, self._rect[3])
        if self._rect[3] < 0:
            self._rect = (self._rect[0], self._rect[1], self._rect[2], 0)

    @property
    def rect(self):
        return self._rect
