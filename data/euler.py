from threading import Thread


def euler_method(big_step, system, state_vec, time_vec, dt, sim_length,
                 interference):
    over = False
    step = 0
    steps_per_frame = round(0.01 / dt)
    A_sys = system
    x1, x2, x3, x4 = state_vec
    t_vec = time_vec

    while True:
        k = big_step + step
        if k >= sim_length-1:
            over = True
            return over, x1[k], x2[k], x3[k], x4[k]

        step += 1
        if step == 1:
            x4[k] += interference

        x1[k+1] = x1[k] + dt*(
            x1[k]*A_sys[0, 0] + x2[k]*A_sys[0, 1]
            + x3[k]*A_sys[0, 2] + x4[k]*A_sys[0, 3]
        )
        x2[k+1] = x2[k] + dt*(
            x1[k]*A_sys[1, 0] + x2[k]*A_sys[1, 1]
            + x3[k]*A_sys[1, 2] + x4[k]*A_sys[1, 3]
        )
        x3[k+1] = x3[k] + dt*(
            x1[k]*A_sys[2, 0] + x2[k]*A_sys[2, 1]
            + x3[k]*A_sys[2, 2] + x4[k]*A_sys[2, 3]
        )
        x4[k+1] = x4[k] + dt*(
            x1[k]*A_sys[3, 0] + x2[k]*A_sys[3, 1]
            + x3[k]*A_sys[3, 2] + x4[k]*A_sys[3, 3]
        )

        t_vec[k+1] = t_vec[k] + dt

        if step >= steps_per_frame:
            return over, x1[k], x2[k], x3[k], x4[k]


class EulerThread(Thread):
    """Subclass of Thread

    join-Method shall return the result of the Euler-Method after every big
    step. Every big step represent one frame. Within every frame a thread of
    Euler-Method shall calculate the state values x1, x2, x3, x4 due very tiny
    time steps.
    """

    def __init__(self, group=None, target=euler_method, name='EulerThread',
                 args=(), kwargs={}, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name,
                        args=args, kwargs=kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return
