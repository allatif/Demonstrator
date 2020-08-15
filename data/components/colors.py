# NORMAL COLORS (RGB)
PUREWHITE = (255, 255, 255)

WHITE = (240, 240, 240)
BLACK = (0, 0, 0)

GREY = (100, 100, 100)
LGREY = (180, 180, 180)
DGREY = (64, 64, 64)

ORANGE = (255, 165, 0)
ORANGE_PACK = {
    'intro': ORANGE,
    'contrast': (255, 140, 0),
    'shadow': (125, 81, 0)
}

CORAL = (255, 127, 80)
TOMATO = (255, 99, 71)
CORAL_PACK = {
    'intro': CORAL,
    'contrast': TOMATO,
}

RED = (225, 0, 0)
LRED = (200, 55, 55)
DRED = (125, 0, 0)
RED_PACK = {
    'intro': LRED,
    'contrast': RED,
    'light': (228, 88, 88),
    'shadow': DRED,
}

GREEN = (0, 225, 0)
LGREEN = (0, 250, 154)
LLGREEN = (0, 255, 127)
GREEN_PACK = {
    'intro': LLGREEN,
    'contrast': LGREEN,
    'light': (0, 255, 203),
}

BLUE = (0, 0, 225)
LBLUE = (30, 144, 255)
BLUE_PACK = {
    'intro': LBLUE,
    'contrast': BLUE,
    'light': (62, 177, 255),
    'shadow': (0, 0, 128),
    'night': (0, 0, 45)
}

CYAN = (114, 247, 218)


# ALPHA COLORS (RGBA)
_RGB = (0, 0, 0)
TRAN100 = (*_RGB, 100)
TRAN150 = (*_RGB, 150)
TRAN200 = (*_RGB, 200)
TRAN225 = (*_RGB, 225)

A64RED = (*RED, 64)
ARED = (*RED, 128)
ADDBLUE = (*BLUE_PACK['night'], 128)

A200DDBLUE = (*BLUE_PACK['night'], 200)


# COLORS FOR PYPLOT


def get_pp(color):
    """Returns a RGBA tuple with values within 0-1 range

    Needed for applying colors in pyplot.
    """

    _range = 255
    _rgba = []
    for e in color:
        _rgba.append(e/_range)
    return tuple(_rgba)
