from . import pg_init, pg_root
from . states import polemap, euler


def main():
    """Add states to control here."""
    pgapp = pg_root.PygameApp(pg_init.ORIGINAL_CAPTION)
    state_dict = {"POLEMAP": polemap.PoleMap(),
                  "EULER": euler.Euler()}
    pgapp.setup_states(state_dict, "POLEMAP")
    pgapp.run()
