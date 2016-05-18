from typing import Sequence, Iterable, Callable, List
from functools import reduce, partial
import operator as op
import itertools
import os
import multiprocessing as mp

import numpy as np
import scipy.spatial.distance


def _task(fn: Callable, data: Iterable) -> List:
    try:
        return list(map(fn, data))
    except (RuntimeError, TypeError):
        return list(itertools.starmap(fn, data))


def _to_batches(data: Sequence, n: int) -> List[Sequence]:
    batch_size = len(data) // n
    return tuple(data[i: i+batch_size] for i in range(0, len(data), batch_size))


def pwmatrix(func: Callable, data: Sequence, dist=True) -> np.ndarray:
    pairs = list(itertools.combinations(data, 2))
    batches = list(zip(itertools.repeat(func), _to_batches(pairs, N_JOBS)))
    results = scipy.spatial.distance.squareform(
        reduce(op.iadd, WORKERKS.starmap(_task, batches)))
    return results if dist else results + np.identity(len(data))


# initialise the CPU pool
N_JOBS = int(os.getenv("PWM_JOBS", 1))
# WORKERS = joblib.Parallel(n_jobs=N_JOBS, pre_dispatch=1, batch_size=1)
WORKERKS = mp.Pool(processes=N_JOBS)


if __name__ == "__main__":
    # TODO write a proper unit-test
    fn = scipy.spatial.distance.correlation
    data = np.repeat(np.arange(100), 1000).reshape((100, 1000)).T
    print(pwmatrix(fn, data, dist=False))
