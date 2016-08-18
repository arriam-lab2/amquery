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
from lib.kmerize.sample import Sample, get_sample_name
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

        return PwMatrix(config, sample_map, dataframe,
                        distances[config.dist.func])


    @staticmethod
    def load(config: Config):
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
        self.__sample_map.save()

        self.config = config


    def add_samples(self, sample_files: List[str]) -> List[Sample]:
        return [self.add_sample(sample_file) for sample_file in sample_files]


    def add_sample(self, sample_file: str) -> Sample:
        sample_name = get_sample_name(sample_file)

        if not sample_name in self.labels:
            initvalues = [np.nan for x in range(len(self.__dataframe))]
            self.__dataframe[sample_name] = pd.Series(initvalues,
                                                      index=self.__dataframe.index)
            self.__dataframe.loc[sample_name] = initvalues + [np.nan]

            new_sample = KmerCounter.kmerize(self.config, sample_file)
            self.__sample_map[sample_name] = new_sample
            return new_sample
        else:
            return self.sample_map[sample_name]


    def __getitem__(self, pair):
        a, b = pair

        for x in [a, b]:
            if not x.sample_name in self.labels:
                self.add(x)

        if np.isnan(self.dataframe[a.sample_name][b.sample_name]):
            value = LoadApply(self.__distfunc)(a.kmer_index,
                                               b.kmer_index)

            self.__dataframe[a.sample_name][b.sample_name] = value

        return self.dataframe[a.sample_name][b.sample_name]


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
                 queue: mp.Queue):
        self.func = func
        self.queue = queue

    def __call__(self, args):
        a, b = args
        self.queue.put(a)
        return self.func(a, b)


if __name__ == "__main__":
    raise RuntimeError
else:
    pool = mp.Pool(processes=N_JOBS)
    manager = mp.Manager()
    queue = manager.Queue()