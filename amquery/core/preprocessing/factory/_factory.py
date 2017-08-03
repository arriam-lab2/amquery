from amquery.core.distance import FFP_JSD, WEIGHTED_UNIFRAC
from amquery.core.preprocessing import KmerCounter, DummyPreprocessor


class Factory:
    @staticmethod
    def create(config):
        """
        :param config: Config
        :return: Preprocessor 
        """
        method = config.get('distance', 'method')
        if method == FFP_JSD:
            kmer_size = int(config.get('distance', 'kmer_size'))
            return KmerCounter(kmer_size)
        elif method == WEIGHTED_UNIFRAC:
            return DummyPreprocessor()
