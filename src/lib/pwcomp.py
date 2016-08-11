from typing import Sequence, Callable, List, Mapping
import itertools
import numpy as np
import scipy.spatial.distance
import multiprocessing as mp

from .work import N_JOBS
from .ui import progress_bar
from .config import Config
from .metrics import distances


class PackedTask:
    def __init__(self, func: Callable, queue: mp.Queue):
        self.func = func
        self.queue = queue

    def __call__(self, args):
        a, b = args
        self.queue.put(a)
        return self.func(a, b)


class PwMatrix:
    def __init__(self, labels: List[str], matrix: np.ndarray,
                 filename: str, distance_func: Callable):
        self.__labels = labels
        self.__matrix = matrix
        self.__filename = filename
        self.__distfunc = distance_func

    @staticmethod
    def load(config: Config, filename: str):
        matrix = []
        with open(filename) as f:
            labels = f.readline()[:-1].split("\t")[1:]

            for line in f.readlines():
                values = line[:-1].split("\t")[1:]
                matrix.append(values)

            matrix = [list(map(float, l)) for l in matrix]


        distance_func = distances[config.dist.func]
        return PwMatrix(labels, np.matrix(matrix), filename,
                        distance_func)


    def save(self):
        with open(self.__filename, "w") as f:
            print("", *map(str, self.__labels), sep="\t", file=f)
            for label, row in zip(self.__labels, self.__matrix):
                print(label, *map(str, row), sep="\t", file=f)

    def add(self, new_samples: Mapping[str, str]):
        raise NotImplementedError("")
        all_labels = pwmatrix.labels + new_labels
        old_pairs = list(itertools.combinations(pwmatrix.labels, 2))
        new_pairs = [x for x in list(itertools.combinations(all_labels, 2))
                     if not x in old_pairs]

        packed_task = PackedTask(self.__distfunc, queue)
        result = pool.map_async(packed_task, pairs)
        progress_bar(result, queue, len(pairs))



    def __getitem__(self, row, column):
        i = self.__labels.index(row)
        j = self.__labels.index(column)
        return self.__matrix[i, j]


class PairwiseDistance:

    @staticmethod
    def calculate(func: Callable, mapping: Mapping[str, str]) -> PwMatrix:
        pairs = list(itertools.combinations(mapping.values(), 2))
        f = Job(func, queue)
        result = pool.map_async(f, pairs)
        progress_bar(result, queue, len(pairs))
        matrix = scipy.spatial.distance.squareform(result.get())
        return PwMatrix(mapping.keys(), matrix)




if __name__ == "__main__":
    raise RuntimeError
else:
    pool = mp.Pool(processes=N_JOBS)
    manager = mp.Manager()
    queue = manager.Queue()
