from typing import Callable, Iterable, List
import itertools
import multiprocessing as mp

from api.utils.decorators import singleton


@singleton
class Pool:
    def __init__(self, **kwargs):
        self.pool = mp.Pool(processes=kwargs.get("jobs", 1))
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
