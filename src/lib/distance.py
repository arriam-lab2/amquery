from typing import Sequence, Callable, List, Mapping
import itertools
import numpy as np
import scipy.spatial.distance
import multiprocessing as mp
from collections import Counter
from Bio import SeqIO
import functools

from .work import N_JOBS
from .ui import progress_bar
from .config import Config
from .metrics import distances
from .sample_map import SampleMap


class LoadApply:
    def __init__(self, func: Callable):
        self.func = func

    def __call__(self, x_kmer_file: str, y_kmer_file: str):
        xcounter = LoadApply._load_kmer_index(x_kmer_file)
        ycounter = LoadApply._load_kmer_index(y_kmer_file)
        return self.func(xcounter, ycounter)

    @staticmethod
    @functools.lru_cache(maxsize=32)
    def _load_kmer_index(counter_file: str) -> Counter:
        counter = Counter()
        seqs = SeqIO.parse(open(counter_file), "fasta")
        for seq_record in seqs:
            count, sequence = seq_record.id, str(seq_record.seq)
            counter[sequence] = int(count)

        return counter


class PwMatrix:
    def __init__(self, sample_map: SampleMap, matrix: np.ndarray,
                 filename: str, distance_func: Callable):
        self.__sample_map = sample_map
        self.__matrix = matrix
        self.__filename = filename
        self.__distfunc = distance_func

    @staticmethod
    def calculate(config: Config, sample_map: SampleMap):
        pairs = list(itertools.combinations(sample_map.paths, 2))
        distance_func = distances[config.dist.func]

        packed_task = PackedTask(LoadApply(distance_func), queue)

        result = pool.map_async(packed_task, pairs)
        progress_bar(result, queue, len(pairs))

        matrix = scipy.spatial.distance.squareform(result.get())
        return PwMatrix(sample_map, matrix, config.pwmatrix_path,
                        distances[config.dist.func])

    def recalc(self):
        pairs = list(itertools.combinations(self.sample_map.paths, 2))
        distance_func = distances[self.config.dist.func]

        packed_task = PackedTask(LoadApply(distance_func), self, queue)

        result = pool.map_async(packed_task, pairs)
        progress_bar(result, queue, len(pairs))

        matrix = scipy.spatial.distance.squareform(result.get())
        self = PwMatrix(self.sample_map, matrix, self.config.pwmatrix_path,
                        distances[config.selfdist.func])

    @staticmethod
    def load(config: Config, sample_map: SampleMap = None):
        if not sample_map:
            sample_map = SampleMap.load(config)

        filename = config.pwmatrix_path
        matrix = []
        with open(filename) as f:
            labels = f.readline()[:-1].split("\t")[1:]

            for line in f.readlines():
                values = line[:-1].split("\t")[1:]
                matrix.append(values)

            matrix = [list(map(float, l)) for l in matrix]


        distance_func = distances[config.dist.func]
        return PwMatrix(sample_map, np.matrix(matrix), filename,
                        distance_func)


    def save(self):
        labels = self.__sample_map.labels
        with open(self.__filename, "w") as f:
            print("", *map(str, labels), sep="\t", file=f)
            for label, row in zip(labels, self.__matrix):
                print(label, *map(str, row), sep="\t", file=f)


    def __getitem__(self, row, column):
        self.has_to_recalc = False
        for sample in [row, column]:
            if not sample in self.__labels:
                self.__sample_map.register([sample])
                self.has_to_recalc = True

        if self.has_to_recalc:
            self.recalc()
            self.save()

        i = self.__labels.index(row)
        j = self.__labels.index(column)
        return self.__matrix[i, j]

    @property
    def sample_map(self) -> SampleMap:
        return self.__sample_map

    @property
    def labels(self) -> List[str]:
        return self.sample_map.labels

    @property
    def matrix(self) -> np.matrix:
        return self.__matrix

    @property
    def hasvalue(self, a: str, b: str) -> bool:
        return a in self.labels and b in self.labels


class PackedTask:
    def __init__(self,
                 func: Callable,
                 queue: mp.Queue,
                 precalc: PwMatrix = None):
        self.func = func
        self.queue = queue
        self.precalc = precalc

    def __call__(self, args):
        a, b = args
        self.queue.put(a)
        if self.precalc and self.precalc.hasvalue(a, b):
            return self.precalc[a, b]

        return self.func(a, b)


if __name__ == "__main__":
    raise RuntimeError
else:
    pool = mp.Pool(processes=N_JOBS)
    manager = mp.Manager()
    queue = manager.Queue()
