import os
import abc
from amquery.core.distance.factory import Factory as DistanceFactory
from amquery.core.preprocessing.factory import Factory as PreprocessorFactory
from amquery.core.biom import merge_biom_tables
from amquery.core.storage.factory import Factory as StorageFactory
from amquery.utils.config import read_config
from amquery.core.sample import Sample
from amquery.utils.split_fasta import split_fasta
from amquery.utils.config import get_sample_dir


class SampleReference:
    @abc.abstractmethod
    def name(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def content(self):
        raise NotImplementedError()


class SampleCollection:
    @abc.abstractmethod
    def __getitem__(self, item):
        """
        :param item: SampleReference 
        :return: Sample
        """
        raise NotImplementedError()


class Index:
    def __init__(self, distance, preprocessor, storage):
        """
        :param distance: SampleDistance
        :param preprocessor: Preprocessor
        :param storage: MetricIndexStorage
        """
        self._distance = distance
        self._preprocessor = preprocessor
        self._storage = storage

    def __len__(self):
        """
        :return: int 
        """
        return len(self._storage) if self._storage else 0

    @staticmethod
    def init(config):
        """
        :return: Index
        """
        distance = DistanceFactory.create(config)
        preprocessor = PreprocessorFactory.create(config)
        storage = StorageFactory.create(config)
        return Index(distance, preprocessor, storage)

    #@measure_time(enabled=True)
    def save(self):
        self.distance.save()
        self.storage.save()

    @staticmethod
    def _load():
        config = read_config()
        distance = DistanceFactory.load(config)
        preprocessor = PreprocessorFactory.create(config)
        storage = StorageFactory.load(config)
        return distance, preprocessor, storage, config

    @staticmethod
    def load():
        distance, preprocessor, storage, config = Index._load()
        return Index(distance, preprocessor, storage), config

    def _reload(self):
        distance, preprocessor, storage, config = Index._load()
        self._distance = distance
        self._preprocessor = preprocessor
        self._storage = storage

    def build(self, config, input_files):
        """
        :param config: configparser.ConfigParser
        :param input_file: Sequence[str]
        :return:
        """
        assert (len(input_files) == 1)
        input_file = input_files[0]

        samples = [Sample(sample_file) for sample_file in split_fasta(input_file, get_sample_dir())]
        processed_samples = [self._preprocessor(sample) for sample in samples]
        self.distance.add_samples(processed_samples)
        self.storage.build(self.distance, processed_samples)

    def refine(self):
        raise NotImplementedError

    def add(self, config, input_files):
        """
        :param config: configparser.ConfigParser
        :param sample_files: Sequence[str] 
        :return: None
        """
        #assert (len(input_files) == 1)
        #input_file = input_files[0]

        # update biom table if present
        if config.has_option("distance", "biom_table"):
            master_table = config.get("distance", "biom_table")
            additional_table = config.get("additional", "biom_table")
            merge_biom_tables(master_table, additional_table)
            self._reload()

        #samples = [Sample(sample_file) for sample_file in split_fasta(input_file, get_sample_dir())]
        samples = [Sample(sample_file) for sample_file in input_files]
        processed_samples = [self._preprocessor(sample) for sample in samples]

        self.distance.add_samples(processed_samples)
        self.storage.add_samples(processed_samples, self.distance)


    def find(self, sample_name, k):
        """
        :param sample_name: str 
        :param k: int
        :return: Tuple[Sequence[np.float], Sequence[np.str]]
        """

        if sample_name in self.distance.labels:
            processed_samples = [self.distance.sample_map[sample_name]]
        else:
            samples = [Sample(sample_file) for sample_file in split_fasta(sample_name, get_sample_dir())]
            processed_samples = [self._preprocessor(sample) for sample in samples]

        return self.storage.find(self.distance, processed_samples[0], k)

    @property
    def distance(self):
        """
        :return: PairwiseDistance 
        """
        return self._distance

    @property
    def storage(self):
        """
        :return: Storage 
        """
        return self._storage

    @property
    def samples(self):
        """
        :return: Sequence[Sample]
        """
        return list(self.distance.sample_map.values())
