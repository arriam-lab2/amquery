import numpy as np


class SparseArray:

    def __init__(self, cols: np.array, data: np.array):
        self.cols = cols
        self.data = data

    def __len__(self):
        return len(self.cols)
