class MouseControl:

    _pos_list = []

    def __init__(self, sensibility):
        self._sens = sensibility
        self.incontrol = False

    def update(self, mouse):
        MouseControl._pos_list.append(mouse)
        if len(MouseControl._pos_list) >= 3:
            del MouseControl._pos_list[0]

    def get_horz_speed(self):
        if len(MouseControl._pos_list) == 2:
            old_pos_x = MouseControl._pos_list[0][0]
            new_pos_x = MouseControl._pos_list[1][0]
            return ((new_pos_x-old_pos_x) / 100)*self._sens
        return 0.0

    def get_positions(self):
        return MouseControl._pos_list
