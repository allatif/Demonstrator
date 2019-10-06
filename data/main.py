from . import pg_init, pg_root
from . states import polemap, game


def main():
    """Add states to control here."""
    pgapp = pg_root.PygameApp(pg_init.ORIGINAL_CAPTION)
    state_dict = {"POLEMAP": polemap.PoleMap(),
                  "GAME": game.Game()}
    pgapp.setup_states(state_dict, "POLEMAP")
    pgapp.run()
