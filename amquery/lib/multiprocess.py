from typing import Callable, Iterable, List
import itertools
import os
import multiprocessing as mp

from amquery.lib.utils import singleton

N_JOBS = int(os.getenv("PWM_JOBS", 1))


@singleton
class Pool:
    def __init__(self):
        self.pool = mp.Pool(processes=N_JOBS)
        self.manager = mp.Manager()
        self.queue = self.manager.Queue()

    def map_async(self, *args):
        return self.pool.map_async(*args)

    def clear(self):
        while not self.queue.empty():
            self.queue.get()


class PackedUnaryFunction:
    def __init__(self,
                 func: Callable,
                 queue: mp.Queue):
        self.func = func
        self.queue = queue

    def __call__(self, arg):
        self.queue.put(1)
        return self.func(arg)


class PackedBinaryFunction:
    def __init__(self,
                 func: Callable,
                 queue: mp.Queue):
        self.func = func
        self.queue = queue

    def __call__(self, args):
        a, b = args
        self.queue.put(1)
        return self.func(a, b)


def run(fn: Callable, data: Iterable) -> List:
    try:
        return list(map(fn, data))
    except (RuntimeError, TypeError):
        return list(itertools.starmap(fn, data))
