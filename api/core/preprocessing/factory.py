from api.core.distance import FFP_JSD, WEIGHTED_UNIFRAC
from api.core.preprocessing import KmerCounter, DummyPreprocessor


class Factory:
    @staticmethod
    def create(database_config):
        """
        :param database_config: dict
        :return: Preprocessor 
        """
        method = database_config['distance']

        if method == FFP_JSD:
            kmer_size = int(database_config['kmer_size'])
            return KmerCounter(kmer_size)
        elif method == WEIGHTED_UNIFRAC:
            return DummyPreprocessor()
