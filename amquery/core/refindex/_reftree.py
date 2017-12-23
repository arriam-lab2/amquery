"""
Metric index of reference database
"""


from amquery.core.sample import Sample
from amquery.core.preprocessing.kmer_counter import KmerCounter
from amquery.core.distance import distances, FFP_JSD
from amquery.core.storage import VpTree
from amquery.utils.config import get_sample_dir
from amquery.utils.split_fasta import split_fasta


class ReferenceTree:
    def __init__(self, distance, preprocessor, storage, reference_files):
        """
        :param distance: SampleDistance
        :param preprocessor: Preprocessor
        :param storage: MetricIndexStorage
        """
        self._distance = distance
        self._preprocessor = preprocessor
        self._storage = storage
        self._reference_files = reference_files


    @staticmethod
    def create(database_config):
        """
        :param database_config: dict
        :return: ReferenceTree
        """
        assert 'kmer_size' in database_config
        assert 'rep_tree' in database_config

        kmer_size = database_config['kmer_size']
        reference_files = database_config['rep_tree']

        distance = distances[FFP_JSD]
        preprocessor = KmerCounter(kmer_size)
        storage = VpTree()
        return ReferenceTree(distance, preprocessor, storage, reference_files)

    @staticmethod
    def load(database_config):
        """
        :param database_config: dict
        :return: ReferenceTree
        """
        raise NotImplementedError()

    def build(self):
        """
        :param input_file: str
        :return: None
        """

        samples = [Sample(sample_file) for sample_file in split_fasta(input_file, get_sample_dir())]
        processed_samples = [self._preprocessor(sample) for sample in samples]
        self._distance.add_samples(processed_samples)
        self._storage.build(self._distance, processed_samples)