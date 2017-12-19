import yack
from amquery.core.preprocessing import Preprocessor


class KmerCounter(Preprocessor):
    def __init__(self, k):
        self.k = k

    def __call__(self, sample):
        """
        :param sample: Sample
        :return: Sample
        """
        counted = yack.count_kmers(sample.sequences(), self.k)
        counted.normalize()
        sample.set_kmer_index(counted)
        return sample
