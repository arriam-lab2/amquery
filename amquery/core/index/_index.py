import abc

from amquery.core.distance.factory import Factory as DistanceFactory
from amquery.core.preprocessing.factory import Factory as PreprocessorFactory
from amquery.core.storage.factory import Factory as StorageFactory
from amquery.core.storage import Storage
from amquery.core.sample import Sample
from amquery.utils.config import read_config


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
    def __init__(self, distance, storage):
        """
        :param distance: SampleDistance
        :param storage: MetricIndexStorage
        """
        self._distance = distance
        self._storage = storage

    #@measure_time(enabled=True)
    def save(self):
        self.distance.save()
        self.storage.save()

    @staticmethod
    #@measure_time(enabled=True)
    def load(config):
        distance = SamplePairwiseDistance.load(config)
        storage = Storage.load(config)
        return Index(distance, storage)

    @staticmethod
    def build(sample_files):
        config = read_config()

        distance = DistanceFactory.create(config)
        preprocessor = PreprocessorFactory.create(config)
        storage = StorageFactory.create(config)

        samples = [Sample(sample_file) for sample_file in sample_files]
        processed_samples = [preprocessor(sample) for sample in samples]
        storage.build(distance, processed_samples)
        return Index(distance, storage)

        #sample_map = SampleMap(kmerize_samples(sample_files, config.dist.kmer_size))
        #pwmatrix = PwMatrix.create(sample_map)
        #tree_distance = TreeDistance(pwmatrix)
        #vptree = VpTree(config).build(tree_distance)
        #return Index(pwmatrix, vptree)

    def refine(self):
        self._pwmatrix = PwMatrix.create(self.config, self.pwmatrix.sample_map)
        tree_distance = TreeDistance(self.pwmatrix)
        self._vptree = VpTree(self.config).build(tree_distance)

    def add(self, sample_files):
        sample_map = SampleMap(self.config,
                               kmerize_samples(sample_files,
                                               self.config.dist.kmer_size)
                               )

        self.sample_map.update(sample_map)
        tree_distance = TreeDistance(self.pwmatrix)
        self.vptree.add_samples(sample_map.values(), tree_distance)

    def find(self, sample_file: str, k: int):
        sample_map = SampleMap(self.config,
                               kmerize_samples([sample_file],
                                               self.config.dist.kmer_size)
                               )
        sample = list(sample_map.values())[0]

        tree_distance = TreeDistance(self.pwmatrix)
        values, points = self.vptree.search(sample, k, tree_distance)
        return values, points

    @property
    def config(self):
        return self._config

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
