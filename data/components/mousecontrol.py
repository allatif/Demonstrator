class MouseControl:

    _pos_list = []

    def __init__(self, sensibility):
        self._sens = sensibility
        self.incontrol = False

    def update(self, mouse):
        MouseControl._pos_list.append(mouse)
        if len(MouseControl._pos_list) >= 3:
            del MouseControl._pos_list[0]

    def get_horz_force(self):
        max_force = 100_000
        if len(MouseControl._pos_list) == 2:
            old_pos_x = MouseControl._pos_list[0][0]
            new_pos_x = MouseControl._pos_list[1][0]
            force = (new_pos_x-old_pos_x)*self._sens
            if abs(force) > max_force:
                return (force/abs(force))*max_force
            return force
        return 0.0

    def get_positions(self):
        return MouseControl._pos_list
