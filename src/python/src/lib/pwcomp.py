from typing import Sequence, Callable
import multiprocessing as mp
import itertools
import numpy as np
import scipy.spatial.distance
import time
from tqdm import tqdm

from .work import N_JOBS


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
    n = len(pairs)

    f = Job(func, queue)
    result = pool.map_async(f, pairs)

    # progress bar loop
    with tqdm(total=n) as pbar:
        prev = 0

        while not result.ready():
            size = queue.qsize()
            k = size - prev
            if k > 0:
                pbar.update(k)
                prev = size
            time.sleep(1)

        k = queue.qsize() - prev
        if k > 0:
            pbar.update(k)

    return scipy.spatial.distance.squareform(result.get())

    #results = scipy.spatial.distance.squareform(
    #    workers.starmap(func, pairs))
    #return results if dist else results + np.identity(len(data))



if __name__ == "__main__":
    raise RuntimeError
else:
    pool = mp.Pool(processes=N_JOBS)
    manager = mp.Manager()
    queue = manager.Queue()
