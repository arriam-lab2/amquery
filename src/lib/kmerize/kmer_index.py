import numpy as np
import pickle
from collections import Counter

from lib.config import Config
from lib.kmerize.sample import Sample


class OrderedSet():
    def __init__(self):
        self.map = {}
        self.counter = -1

    def setdefault(self, key):
        if key not in self.map:
            self.counter += 1
            self.map[key] = self.counter

        return self.map[key]

    def __len__(self):
        return len(self.map)


def _kmerize_string(string: str, k: int):
                    # compression: int=9):)
    byte_string = bytes(string, encoding="utf8")
    return (byte_string[i:i+k] for i in range(len(string)-k+1))


class PrimaryKmerIndex:
    def __init__(self, config: Config):
        self.config = config
        self.kmer_set = OrderedSet()

    @staticmethod
    def load(config: Config):
        with open(config.primary_kmer_index_path, 'rb') as f:
            kmer_index = pickle.load(f)
            kmer_index.config = config
            return kmer_index

    def save(self):
        config = self.config
        del self.config
        pickle.dump(self, open(config.primary_kmer_index_path, "wb"))
        self.config = config

    def register(self, sample: Sample):
        k = self.config.dist.kmer_size
        kmer_primary_refs = [self.kmer_set.setdefault(kmer)
                             for seq in sample.sequences()
                             for kmer in _kmerize_string(seq, k)]

        kmer_ref_counter = Counter(kmer_primary_refs)

        sample.kmers_distribution = np.zeros(len(self.kmer_set))
        for kmer_ref, count in kmer_ref_counter.items():
            sample.kmers_distribution[kmer_ref] = count

    def extend_sample_distribution(self, sample: Sample):
        zeros = np.zeros(len(self.kmer_set) - len(sample.kmers_distribution))
        sample.kmers_distribution = np.concatenate((sample.kmers_distribution,
                                                   zeros))
