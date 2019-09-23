import numpy as np


class StateSpaceCnt:

    def __init__(self, c1, c2, c3, c4):
        self.ss_Cnt = np.matrix([c1, c2, c3, c4])
