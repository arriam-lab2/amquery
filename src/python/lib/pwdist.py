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


def pwdist(func: Callable, data: Sequence) -> np.ndarray:
    batches = list(zip(itertools.repeat(func), _to_batches(data, N_JOBS)))
    results = WORKERKS.starmap(_task, batches)
    return scipy.spatial.distance.squareform(reduce(op.iadd, results))


# initialise the CPU pool
N_JOBS = int(os.getenv("PWDIST_JOBS", 1))
# WORKERS = joblib.Parallel(n_jobs=N_JOBS, pre_dispatch=1, batch_size=1)
WORKERKS = mp.Pool(processes=N_JOBS)


if __name__ == "__main__":
    # TODO write a proper unit-test
    fn = scipy.spatial.distance.correlation
    data = list(itertools.combinations(
        np.repeat(np.arange(100), 1000).reshape((100, 1000)).T, 2))
    print(pwdist(fn, data))
