from typing import Sequence, Callable, List, Mapping
import itertools
import numpy as np
import pandas as pd
import scipy.spatial.distance
import multiprocessing as mp
from collections import Counter
from Bio import SeqIO
import functools

from .work import N_JOBS
from .ui import progress_bar
from .config import Config
from .metrics import distances
from lib.kmerize.sample_map import SampleMap
from lib.kmerize.sample import get_sample_name
from lib.kmerize.kmer_counter import KmerCounter


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
    def __init__(self,
                 config: Config,
                 sample_map: SampleMap,
                 dataframe: pd.DataFrame,
                 distance_func: Callable):

        self.config = config
        self.__sample_map = sample_map
        self.__dataframe = dataframe
        self.__distfunc = distance_func

    @staticmethod
    def create(config: Config, input_files: List[str]):
        sample_map = SampleMap.create(config, input_files)

        pairs = list(itertools.combinations(sample_map.paths, 2))
        distance_func = distances[config.dist.func]

        packed_task = PackedTask(LoadApply(distance_func), queue)

        result = pool.map_async(packed_task, pairs)
        progress_bar(result, queue, len(pairs))

        matrix = scipy.spatial.distance.squareform(result.get())
        dataframe = pd.DataFrame(matrix,
                                 index=sample_map.labels,
                                 columns=sample_map.labels)
        print(dataframe)
        return PwMatrix(config, sample_map, dataframe,
                        distances[config.dist.func])


    @staticmethod
    def load(config: Config, sample_map: SampleMap = None):
        if not sample_map:
            sample_map = SampleMap.load(config)

        dataframe = pd.read_csv(config.pwmatrix_path, sep='\t', index_col=0)
        distance_func = distances[config.dist.func]
        pwmatrix = PwMatrix(config,
                            sample_map,
                            dataframe,
                            distance_func)
        return pwmatrix


    def save(self):
        config = self.config
        del self.config

        self.__dataframe.to_csv(config.pwmatrix_path, sep='\t')

        self.config = config


    def add(self, samples: List[str]) -> List[str]:
        result = []

        for sample in samples:
            if not sample in self.labels:
                sample_name = get_sample_name(sample)
                self.__add_sample(sample_name)
                print("KMERIZING", sample)
                new_sample = KmerCounter.kmerize(self.config, sample)
                self.__sample_map[sample_name] = new_sample
                result.append(sample_name)
            else:
                result.append(sample)

        return result


    def __add_sample(self, sample_name) -> int:
        initvalues = [np.nan for x in range(len(self.__dataframe))]
        self.__dataframe[sample_name] = pd.Series(initvalues,
                                                  index=self.__dataframe.index)

        self.__dataframe.loc[sample_name] = initvalues + [np.nan]


    def __getitem__(self, pair):
        row, column = self.add([*pair])

        print(self.labels)
        print(self.matrix)
        i = list(self.labels).index(row)
        j = list(self.labels).index(column)

        print(i, j)

        if np.isnan(self.matrix[i, j]):
            print("Load apply", row, column)
            self.__matrix[i, j] = LoadApply(self.__distfunc)(self.sample_map[row],
                                                             self.sample_map[column])

        print("PWMATRIX RESULT", self.matrix[i, j], "of", row, column)
        print(self.matrix)
        return self.matrix[i, j]

    @property
    def sample_map(self) -> SampleMap:
        return self.__sample_map

    @property
    def labels(self) -> List[str]:
        return self.__dataframe.columns

    @property
    def dataframe(self) -> pd.DataFrame:
        return self.__dataframe

    @property
    def matrix(self) -> np.ndarray:
        return self.__dataframe.as_matrix()

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
