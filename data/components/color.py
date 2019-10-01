# NORMAL COLORS (RGB)
WHITE = (240, 240, 240)
BLACK = (0, 0, 0)

GREY = (100, 100, 100)
LGREY = (180, 180, 180)
DGREY = (64, 64, 64)

RED = (225, 0, 0)
GREEN = (0, 225, 0)
BLUE = (0, 0, 225)

ORANGE = (255, 127, 80)
TOMATO = (255, 99, 71)

LLRED = (228, 88, 88)
LRED = (200, 55, 55)
DRED = (125, 0, 0)

LBLUE = (30, 144, 255)
DBLUE = (0, 0, 128)
DDBLUE = (0, 0, 45)

# ALPHA COLORS (RGBA)
_RGB = (0, 0, 0)
TRAN100 = (*_RGB, 100)
TRAN150 = (*_RGB, 150)
TRAN200 = (*_RGB, 200)

ARED = (*RED, 128)
ADDBLUE = (*DDBLUE, 128)

A200DDBLUE = (*DDBLUE, 200)


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
