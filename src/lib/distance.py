from typing import Callable, List
import itertools
import numpy as np
import pandas as pd
import scipy.spatial.distance

from .ui import progress_bar
from .config import Config
from .metrics import distances
from src.lib.kmerize.sample_map import SampleMap
from src.lib.kmerize.sample import Sample
from src.lib.benchmarking import measure_time
from src.lib.multiprocess import Pool, PackedBinaryFunction


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
    @measure_time(enabled=True)
    def create(config: Config, sample_map: SampleMap):
        distributions = [x.kmer_index
                         for x in sample_map.samples]
        pairs = list(itertools.combinations(distributions, 2))
        distance_func = distances[config.dist.func]

        packed_task = PackedBinaryFunction(distance_func, Pool.instance().queue)
        result = Pool.instance().map_async(packed_task, pairs)
        progress_bar(result, Pool.instance().queue, len(pairs))

        data = result.get()
        Pool.instance().clear()
        matrix = scipy.spatial.distance.squareform(data)
        dataframe = pd.DataFrame(matrix,
                                 index=sample_map.labels,
                                 columns=sample_map.labels)

        return PwMatrix(config, sample_map, dataframe,
                        distances[config.dist.func])

    @staticmethod
    def load(config: Config):
        sample_map = SampleMap.load(config)
        dataframe = pd.read_csv(config.pwmatrix_path,
                                sep='\t')
        dataframe['id'] = dataframe.keys()
        dataframe = dataframe.set_index('id')
        distance_func = distances[config.dist.func]
        pwmatrix = PwMatrix(config,
                            sample_map,
                            dataframe,
                            distance_func)
        return pwmatrix

    def save(self):
        config = self.config
        del self.config

        self.__dataframe.to_csv(config.pwmatrix_path,
                                sep='\t',
                                na_rep="N/A",
                                index=False)
        self.__sample_map.save()

        self.config = config

    def add_sample(self, sample: Sample) -> Sample:
        if sample.name not in self.labels:
            initvalues = [np.nan for x in range(len(self.__dataframe))]
            self.__dataframe[sample.name] = pd.Series(initvalues,
                                                      index=self.dataframe.index)
            self.__dataframe.loc[sample.name] = initvalues + [np.nan]
            self.__sample_map[sample.name] = sample

    def __getitem__(self, pair):
        a, b = pair

        for x in [a, b]:
            if x.name not in self.labels:
                self.add_sample(x)

        if np.isnan(self.dataframe[a.name][b.name]):
            value = self.__distfunc(a.kmer_index,
                                    b.kmer_index)

            self.__dataframe[a.name][b.name] = value

        return self.dataframe[a.name][b.name]

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
