from typing import Callable, Iterable, List, Sequence
import itertools
import os
import multiprocessing as mp


N_JOBS = int(os.getenv("PWM_JOBS", 1))


def task(fn: Callable, data: Iterable) -> List:
    try:
        return list(map(fn, data))
    except (RuntimeError, TypeError):
        return list(itertools.starmap(fn, data))


def to_batches(data: Sequence, n: int) -> List[Sequence]:
    batch_size = len(data) // n
    return tuple(data[i: i+batch_size]
                 for i in range(0, len(data), batch_size))


if __name__ == "__main__":
    pass
