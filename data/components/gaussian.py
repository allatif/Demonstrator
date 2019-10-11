class Plane:

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._zero_pos_Re = height//2
        self._zero_pos_Im = width//2 + 150

        self.Re_axis = Axis(self._zero_pos_Re, length=self._width,
                            wide=self._height, direc='x')

        self.Im_axis = Axis(self._zero_pos_Im, length=self._height,
                            wide=self._width, direc='y')

    def get_point(self, pos):
        x = (pos[0]-self._zero_pos_Im) / self.Re_axis.get_scale()
        y = (self._zero_pos_Re-pos[1]) / self.Im_axis.get_scale()
        return x, y

    def get_pos_from_point(self, point):
        pos_x = int(round(point[0]*self.Re_axis.get_scale()+self._zero_pos_Im))
        pos_y = int(round(self._zero_pos_Re-point[1]*self.Im_axis.get_scale()))
        return pos_x, pos_y


class Axis:

    positions = []

    def __init__(self, pos, length, wide, direc='x', scale_lvl=2, thickness=2):
        self.pos = pos
        self.length = length
        self.wide = wide
        self.direction = direc

        # pixels that represent 1 unit length
        self._scale_lvl = scale_lvl
        self._scales = [12, 25, 50, 100]
        self._scale = self._scales[scale_lvl]

        self.thickness = thickness
        self._start = (0, 0)
        self._end = (0, 0)

        Axis.positions.append(pos)

        if self.direction == 'x':
            self._start = 0, self.pos
            self._end = self.length, self.pos
        elif self.direction == 'y':
            self._start = self.pos, 0
            self._end = self.pos, self.length

    def get_coordlines(self, grid=False):
        coord_length = 2*self.wide if grid else 10
        coordlines = []
        start = (0, 0)
        end = (0, 0)

        self._scale = self._scales[self._scale_lvl]

        for side in range(0, 2):
            step = -self._scale if side == 0 else self._scale
            zero = Axis.positions[1] if self.direction == 'x' else Axis.positions[0]
            for coord in range(zero, side*self.length, step):
                if self.direction == 'x':
                    start = coord, self.pos-(coord_length//2)
                    end = coord, self.pos+(coord_length//2)
                if self.direction == 'y':
                    start = self.pos-(coord_length//2), coord
                    end = self.pos+(coord_length//2), coord
                coordlines.append((start, end))

        return coordlines

    def zoom(self, dir='in'):
        lvl_amts = len(self._scales)
        if dir == 'in':
            if self._scale_lvl >= lvl_amts-1:
                self._scale_lvl = lvl_amts-1
            else:
                self._scale_lvl += 1
        elif dir == 'out':
            if self._scale_lvl < 1:
                self._scale_lvl = 0
            else:
                self._scale_lvl -= 1

    def get_line(self):
        return self._start, self._end

    def get_scale(self):
        return self._scale

    @staticmethod
    def get_positions():
        return Axis.positions


class Pole:

    def __init__(self, center, radius, Re, Im):
        self._c_x, self._c_y = center
        self._orig_r = radius
        self._r = radius
        self._Re = Re
        self._Im = Im

    def update(self):
        pass

    def shrink(self):
        self._r = round(0.5*self._r)

    def norm(self):
        self._r = self._orig_r

    def pickup(self):
        pass

    def drop(self):
        pass

    def get_center(self):
        return self._c_x, self._c_y

    def mouse_inside(self, mouse):
        return (mouse[0]-self._c_x)**2 + (mouse[1]-self._c_y)**2 < self._r**2

    def is_unstable(self):
        return self._Re > 0

    def is_marginal_stable(self):
        return self._Re <= 0 and self._Re > -0.016

    @property
    def r(self):
        return self._r

    def __str__(self):
        if self._Im > 0:
            return f'{round(self._Re, 3)} +{round(self._Im, 3)}i'
        elif self._Im == 0:
            return f'{round(self._Re, 3)}'
        return f'{round(self._Re, 3)} {round(self._Im, 3)}i'
