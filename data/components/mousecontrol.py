class MouseControl:

    # List of the current and last position of mouse cursor
    # See update() logic
    _pos_list = []

    def __init__(self, sensibility):
        self._sens = sensibility

        self._mouse = (0, 0)
        self._force = 0.0
        self.input = False

    def update(self, mouse):
        self._mouse = mouse
        MouseControl._pos_list.append(mouse)

        if len(MouseControl._pos_list) >= 3:
            del MouseControl._pos_list[0]
        if self.input:
            self._force = self._calc_horizontal_force()
        else:
            self._force = 0

    def _calc_horizontal_force(self):
        max_force = 100_000
        if len(MouseControl._pos_list) == 2:
            old_pos_x = MouseControl._pos_list[0][0]
            new_pos_x = MouseControl._pos_list[1][0]
            force = (new_pos_x-old_pos_x)*self._sens
            if abs(force) > max_force:
                return (force/abs(force))*max_force
            return force
        return 0.0

    @property
    def mouse(self):
        return self._mouse

    @property
    def force(self):
        return self._force
