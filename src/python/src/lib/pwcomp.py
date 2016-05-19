from typing import Sequence, Callable
from functools import reduce
import multiprocessing as mp
import operator as op
import itertools

import numpy as np
import scipy.spatial.distance

from .work import task, to_batches, N_JOBS


def pwmatrix(func: Callable, data: Sequence, dist=True) -> np.ndarray:
    pairs = list(itertools.combinations(data, 2))
    batches = list(zip(itertools.repeat(func), to_batches(pairs, N_JOBS)))
    results = scipy.spatial.distance.squareform(
        reduce(op.iadd, workers.starmap(task, batches)))
    return results if dist else results + np.identity(len(data))


if __name__ == "__main__":
    raise RuntimeError
else:
    workers = mp.Pool(processes=N_JOBS)
