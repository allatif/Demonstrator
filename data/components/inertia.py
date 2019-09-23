class Inertia:

    def __init__(self, mass, body, *args):
        if body == 'sphere':
            radius = args[0]
        elif body == 'hollow_sphere':
            radius = args[0]
            radius_i = args[1]
        self.value = None

        if body == 'sphere':
            self.value = (2/5) * mass * radius**2

        if body == 'hollow_sphere':
            self.value = (
                (2/5) * mass
                * (radius**5 - radius_i**5) / (radius**3 - radius_i**3)
                + mass * radius**2
            )
