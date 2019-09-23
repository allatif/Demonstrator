from time import sleep
from threading import Thread


class Impulse(Thread):

    def __init__(self, group=None, target=None, name='ImpulseWave',
                 args=(), kwargs=None, verbose=None):
        super(Impulse, self).__init__(group=group, target=target, name=name)

        self.running = False
        self._c_x = args[0]
        self._c_y = args[1]
        self.radius = args[2]
        self.width = args[3]
        self._max_radius = 1.2*abs(args[4])
        self._radius_ratio = 0
        self._transparency = 256
        self.dynamic_color = None

    def run(self):
        self.running = True
        while self.running:
            self._radius_ratio = self.radius / self._max_radius
            if self._radius_ratio > 1:
                self._radius_ratio = 1.0

            self.grow(1.03)
            sleep(0.01)

            if self.radius > self._max_radius:
                self.stop()

    def stop(self):
        self.running = False

    def grow(self, rate):
        self.radius = int((self.radius+self.width) * rate)
        self.width = int(self.width * (rate+0.40))
        self._transparency = int(255 - 255*(self._radius_ratio))
        self.dynamic_color = (0, 191, 255, self._transparency)

    def get_center(self):
        return self._c_x, self._c_y
