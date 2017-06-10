import abc
from amquery.core.distance.factory import Factory as DistanceFactory
from amquery.core.preprocessing.factory import Factory as PreprocessorFactory
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
    def init():
        """
        :return: Index
        """
        config = read_config()
        distance = DistanceFactory.create(config)
        preprocessor = PreprocessorFactory.create(config)
        storage = StorageFactory.create(config)
        return Index(distance, preprocessor, storage)

    #@measure_time(enabled=True)
    def save(self):
        self.distance.save()
        self.storage.save()

    @staticmethod
    def load():
        config = read_config()
        distance = DistanceFactory.load(config)
        preprocessor = PreprocessorFactory.create(config)
        storage = StorageFactory.load(config)
        return Index(distance, preprocessor, storage)

    def build(self, input_files):
        """
        :param input_file: Sequence[str]
        :return:
        """
        assert (len(input_files) == 1)

        config = read_config()
        self._distance = DistanceFactory.create(config)
        self._preprocessor = PreprocessorFactory.create(config)
        self._storage = StorageFactory.create(config)

        input_file = input_files[0]
        samples = [Sample(sample_file) for sample_file in split_fasta(input_file, get_sample_dir())]
        processed_samples = [self._preprocessor(sample) for sample in samples]
        self.distance.add_samples(processed_samples)
        self.storage.build(self.distance, processed_samples)


    def refine(self):
        #self._pwmatrix = PwMatrix.create(self.config, self.pwmatrix.sample_map)
        #tree_distance = TreeDistance(self.pwmatrix)
        #self._vptree = VpTree(self.config).build(tree_distance)
        raise NotImplementedError

    def add(self, sample_files):
        """
        :param sample_files: Sequence[str] 
        :return: None
        """
        #processed_samples = [self._preprocessor(Sample(sample_file)) for sample_file in sample_files]
        #self.distance.add_samples(processed_samples)
        #self.storage.add_samples(processed_samples, self.distance)
        raise NotImplementedError

    def find(self, sample_file, k):
        """
        :param sample_file: str 
        :param k: int
        :return: Tuple[Sequence[np.float], Sequence[np.str]]
        """
        #processed_sample = self._preprocessor(Sample(sample_file))
        #return self.storage.find(self.distance, processed_sample, k)
        raise NotImplementedError

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
