import os
import pygame as pg
from . import pg_root


SCREEN_SIZE = (1024, 600)
ORIGINAL_CAPTION = "Kugel-Kegel-Demonstrator"
SCALE = 200  # Pixels that will be equivalent to 1 meter
FPS = (66.0, 110.0)  # Will be 60 or 100 FPS in game

# Initialization
pg.init()
pg.display.set_caption(ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(SCREEN_SIZE)
SCREEN_RECT = SCREEN.get_rect()

# Resource loading
GFX = pg_root.load_all_gfx(os.path.join("resources", "images"))
FONTS = pg_root.load_all_fonts(os.path.join("resources", "fonts"))
