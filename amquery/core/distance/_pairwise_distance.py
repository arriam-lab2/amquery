import abc
import numpy as np
import pandas as pd
from amquery.core.distance.metrics import distances
from amquery.utils.config import get_distance_path


class PairwiseDistance:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __getitem__(self, item):
        """
        :param item: Tuple[Any, Any]
        :return: float
        """
        raise NotImplementedError()


class SamplePairwiseDistanceFunction:
    @abc.abstractmethod
    def __call__(self, a, b):
        """
        :param a: Sample 
        :param b: Sample
        :return: float
        """
        raise NotImplementedError()


class SamplePairwiseDistance(PairwiseDistance):
    def __init__(self, distance_function, dataframe=pd.DataFrame()):
        """
        :param distance_function: SamplePairwiseDistanceFunction
        """
        self._distance_function = distance_function
        self._dataframe = dataframe

    #@classmethod
    #def create(cls, config):
    #    """
    #    :param config: Config
    #    :return: LazyPairwiseDistance
    #    """
    #    #dataframe = pd.DataFrame(index=sample_map.labels, columns=sample_map.labels)
    #    #return cls(config, sample_map, dataframe, distances[config.dist.func])
    #    return cls(distances[config.dist.func])

    @staticmethod
    def load(config):
        """
        :param config: Config 
        :return: SamplePairwiseDistance
        """
        #sample_map = SampleMap.load(config)
        if os.path.exists(get_distance_path()):
            dataframe = pd.read_csv(get_distance_path(), sep='\t')
            dataframe['id'] = dataframe.keys()
            dataframe = dataframe.set_index('id')
        else:
            dataframe = pd.DataFrame()

        method = config.get('distance', 'method')
        return SamplePairwiseDistance(distances[method], dataframe=dataframe)

    def save(self):
        self._dataframe.to_csv(get_distance_path(), sep='\t', na_rep="N/A", index=False)
        #self._sample_map.save()

    def add_sample(self, sample):
        """
        :param sample: Sample 
        :return: None
        """
        if sample.name not in self.labels:
            init_values = [np.nan for x in range(len(self._dataframe))]
            self._dataframe[sample.name] = pd.Series(init_values, index=self.dataframe.index)
            self._dataframe.loc[sample.name] = init_values + [np.nan]
            #self._sample_map[sample.name] = sample

    def __getitem__(self, pair):
        a, b = pair

        for x in [a, b]:
            if x.name not in self.labels:
                self.add_sample(x)

        if np.isnan(self.dataframe[a.name][b.name]):
            value = self._distance_function(a, b)
            self._dataframe[a.name][b.name] = value if not np.isnan(value) else 0.0

        return self.dataframe[a.name][b.name]


    def __call__(self, a, b):
        """
        :param a: Sample 
        :param b: Sample
        :return: float
        """
        return self[a, b]


    @property
    def labels(self):
        return self._dataframe.columns

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def matrix(self) -> np.ndarray:
        return self._dataframe.as_matrix()

    @property
    def hasvalue(self, a: str, b: str) -> bool:
        return a in self.labels and b in self.labels
