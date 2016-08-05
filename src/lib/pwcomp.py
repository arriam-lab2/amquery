from typing import Sequence, Callable
import itertools
import numpy as np
import scipy.spatial.distance
import multiprocessing as mp

from .work import N_JOBS
from .ui import progress_bar


class Job:
    def __init__(self, func: Callable, queue: mp.Queue):
        self.func = func
        self.queue = queue

    def __call__(self, args):
        a, b = args
        self.queue.put(a)
        return self.func(a, b)


def pwmatrix(func: Callable, data: Sequence) -> np.ndarray:
    pairs = list(itertools.combinations(data, 2))
    f = Job(func, queue)
    result = pool.map_async(f, pairs)
    progress_bar(result, queue, len(pairs))
    return scipy.spatial.distance.squareform(result.get())


if __name__ == "__main__":
    raise RuntimeError
else:
    pool = mp.Pool(processes=N_JOBS)
    manager = mp.Manager()
    queue = manager.Queue()
