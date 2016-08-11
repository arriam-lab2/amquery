from typing import Sequence, Callable, List, Mapping
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


class PwMatrix:
    def __init__(self, labels: List[str], matrix: np.ndarray):
        self.labels = labels
        self.matrix = matrix

    def __getitem__(self, row, column):
        i = self.labels.index(row)
        j = self.labels.index(column)
        return self.matrix[i, j]


class PairwiseDistance:
    @staticmethod
    def load(filename: str):
        matrix = []
        with open(filename) as f:
            labels = f.readline()[:-1].split("\t")[1:]

            for line in f.readlines():
                values = line[:-1].split("\t")[1:]
                matrix.append(values)

            matrix = [list(map(float, l)) for l in matrix]

        return PwMatrix(labels, np.matrix(matrix))


    @staticmethod
    def save(pwmatrix: PwMatrix, filename: str):
        labels = pwmatrix.labels
        matrix = pwmatrix.matrix

        with open(filename, "w") as f:
            print("", *map(str, labels), sep="\t", file=f)
            for label, row in zip(labels, matrix):
                print(label, *map(str, row), sep="\t", file=f)


    @staticmethod
    def calculate(func: Callable, mapping: Mapping[str, str]) -> PwMatrix:
        pairs = list(itertools.combinations(mapping.values(), 2))
        f = Job(func, queue)
        result = pool.map_async(f, pairs)
        progress_bar(result, queue, len(pairs))
        matrix = scipy.spatial.distance.squareform(result.get())
        return PwMatrix(mapping.keys(), matrix)

    @staticmethod
    def append(func: Callable, pwmatrix: PwMatrix,
               new_labels: Sequence[str]) -> PwMatrix:

        all_labels = pwmatrix.labels + new_labels
        old_pairs = list(itertools.combinations(pwmatrix.labels, 2))
        new_pairs = [x for x in list(itertools.combinations(all_labels, 2))
                     if not x in old_pairs]

        f = Job(func, queue)
        result = pool.map_async(f, pairs)
        progress_bar(result, queue, len(pairs))
        raise NotImplementedError("")
        #print(result)
        #pwmatrix = scipy.spatial.distance.squareform(result.get())
        return PwMatrix(labels, pwmatrix)


if __name__ == "__main__":
    raise RuntimeError
else:
    pool = mp.Pool(processes=N_JOBS)
    manager = mp.Manager()
    queue = manager.Queue()
