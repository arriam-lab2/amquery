import unittest
from bunch import Bunch
from typing import List, Tuple

from lib.kmerize.kmer_index import PrimaryKmerIndex
from lib.config import Config


class TestKmerize(unittest.TestCase):

    class DummySample:
        def __init__(self, seqs: List[str]):
            self.seqs = seqs
            self.kmer_map = {}

        def sequences(self) -> str:
            for seq in self.seqs:
                yield seq

        def _register_kmer_refs(self, kmer_refs: List[Tuple]):
            self.kmer_map.update(kmer_refs)

    def test_kmerize_sample(self):
        config = Config()
        config.dist = Bunch()
        config.dist.kmer_size = 3

        kmer_index = PrimaryKmerIndex(config)

        seq = 'AAACCCGGGTTT'
        repeats = 10

        sample = self.DummySample([seq] * repeats)
        kmer_index.register(sample)

        distribution = [repeats] * (len(seq) - config.dist.kmer_size + 1)
        self.assertEqual(sample.kmers_distribution, distribution)


if __name__ == '__main__':
    unittest.main()
