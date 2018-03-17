import os
import abc
import numpy as np
import pandas as pd
from amquery.core.distance.metrics import distances
from amquery.core.sample import Sample
from amquery.core.sample_map import SampleMap
from amquery.utils.config import get_distance_path


class PairwiseDistance:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __getitem__(self, item):
        """
        :param item: Tuple[Any, Any]
        :return: float
        """
        raise NotImplementedError


class SamplePairwiseDistance(PairwiseDistance):
    def __init__(self, distance_function,
                 dataframe=pd.DataFrame(), 
                 sample_map=SampleMap()):
        """
        :param distance_function: amquery.core.metrics.SamplePairwiseDistanceFunction
        """
        self._distance_function = distance_function
        self._dataframe = dataframe
        self._sample_map = sample_map

    @staticmethod
    def load(database_config):
        """
        :param database_config: dict
        :return: SamplePairwiseDistance
        """
        database_name = database_config["name"]

        if os.path.exists(get_distance_path(database_name)):
            try:
                dataframe = pd.read_csv(get_distance_path(database_name), sep='\t')
                dataframe['id'] = dataframe.keys()
                dataframe = dataframe.set_index('id')
            except ValueError:
                dataframe = pd.DataFrame()
        else:
            dataframe = pd.DataFrame()

        sample_map = SampleMap.load(database_config)
        method = database_config['distance']
        return SamplePairwiseDistance(distances[method](database_config),
                                      dataframe=dataframe,
                                      sample_map=sample_map)

    def save(self, database_name):
        self._dataframe.to_csv(get_distance_path(database_name), 
                               sep='\t', na_rep="N/A", index=False)
        self._sample_map.save(database_name)

    def add_sample(self, sample):
        """
        :param sample: Sample
        :return: None
        """
        if sample.name not in self.labels:
            init_values = [np.nan for _ in range(len(self._dataframe))]
            self._dataframe[sample.name] = pd.Series(init_values, index=self.dataframe.index)
            self._dataframe.loc[sample.name] = init_values + [np.nan]
            self._sample_map[sample.name] = sample

    def add_samples(self, samples):
        """
        :param samples: Sequence[Sample] 
        :return: None
        """
        for sample in samples:
            self.add_sample(sample)

    def __getitem__(self, pair):
        a, b = pair
        if isinstance(a, np.str) and self._sample_map:
            a = self._sample_map[a]
        if isinstance(b, np.str) and self._sample_map:
            b = self._sample_map[b]

        assert isinstance(a, Sample)
        assert isinstance(b, Sample)

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
        return self[(a, b)]

    @property
    def labels(self):
        return self._dataframe.columns

    @property
    def sample_map(self):
        return self._sample_map

    @property
    def dataframe(self):
        return self._dataframe

    @property
    def matrix(self):
        return self._dataframe.as_matrix()
