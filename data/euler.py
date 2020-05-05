from threading import Thread


def euler_method(A, B, state_vec, t_vec, dt, game_step, control_object=None,
                 interference=0, reference=(0, 0), steps_per_frame=10):
    over = False
    step = 0
    sim_length = len(state_vec[0]) - 1
    x1, x2, x3, x4 = state_vec

    while True:
        k = game_step + step
        if k >= sim_length - 1:
            over = True
            return x1[k], x2[k], x3[k], x4[k], over

        step += 1
        if step == 1:
            x4[k] += interference

        reference_pos, reference_ang = reference

        if control_object is not None:
            x1[k+1] = x1[k] + dt*(
                x1[k]*A[0, 0] + x2[k]*A[0, 1] + x3[k]*A[0, 2] + x4[k]*A[0, 3]
                + B[0]*control_object.force
            )
            x2[k+1] = x2[k] + dt*(
                x1[k]*A[1, 0] + x2[k]*A[1, 1] + x3[k]*A[1, 2] + x4[k]*A[1, 3]
                + B[1]*control_object.force
            )
            x3[k+1] = x3[k] + dt*(
                x1[k]*A[2, 0] + x2[k]*A[2, 1] + x3[k]*A[2, 2] + x4[k]*A[2, 3]
                + B[2]*control_object.force
            )
            x4[k+1] = x4[k] + dt*(
                x1[k]*A[3, 0] + x2[k]*A[3, 1] + x3[k]*A[3, 2] + x4[k]*A[3, 3]
                + B[3]*control_object.force
            )

        else:
            x1[k+1] = x1[k] + dt*(
                x1[k]*A[0, 0] + x2[k]*A[0, 1] + x3[k]*A[0, 2] + x4[k]*A[0, 3]
                - reference_pos*A[0, 0] - reference_ang*A[0, 2]
            )
            x2[k+1] = x2[k] + dt*(
                x1[k]*A[1, 0] + x2[k]*A[1, 1] + x3[k]*A[1, 2] + x4[k]*A[1, 3]
                - reference_pos*A[1, 0] - reference_ang*A[1, 2]
            )
            x3[k+1] = x3[k] + dt*(
                x1[k]*A[2, 0] + x2[k]*A[2, 1] + x3[k]*A[2, 2] + x4[k]*A[2, 3]
                - reference_pos*A[2, 0] - reference_ang*A[2, 2]
            )
            x4[k+1] = x4[k] + dt*(
                x1[k]*A[3, 0] + x2[k]*A[3, 1] + x3[k]*A[3, 2] + x4[k]*A[3, 3]
                - reference_pos*A[3, 0] - reference_ang*A[3, 2]
            )

        t_vec[k+1] = t_vec[k] + dt

        if step >= steps_per_frame:
            return x1[k], x2[k], x3[k], x4[k], over


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
