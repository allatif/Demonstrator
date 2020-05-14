from . import pg_init, pg_root
from . states import splash, main_menu, polemap, neuro, game, menu


def main():
    """Add states to control here."""
    pgapp = pg_root.PygameApp(pg_init.ORIGINAL_CAPTION)
    state_dict = {"SPLASH": splash.Splash(),
                  "MAINSETTINGS": main_menu.MainSetup(),
                  "POLEMAP": polemap.PoleMap(),
                  "NEURO": neuro.Neuro(),
                  "GAME": game.Game(),
                  "SETTINGS": menu.SetupMenu()}
    pgapp.setup_states(state_dict, "SPLASH")
    pgapp.run()
