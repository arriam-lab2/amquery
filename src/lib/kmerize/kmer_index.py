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


def _kmerize_string(string: str, k: int):
                    # compression: int=9):)
    byte_string = bytes(string, encoding="utf8")
    return (byte_string[i:i+k] for i in range(len(string)-k+1))


class PrimaryKmerIndex:
    def __init__(self, config: Config):
        self.config = config
        self.kmer_set = OrderedSet()
        # self.kmer_counter = KmerCounter(config)

    def register(self, sample: Sample):
        k = self.config.dist.kmer_size
        kmer_primary_refs = [(kmer, self.kmer_set.setdefault(kmer))
                             for seq in sample.sequences()
                             for kmer in _kmerize_string(seq, k)]

        kmer_ref_counter = Counter(kmer_primary_refs)

        sorted_by_appereance = sorted(kmer_ref_counter.items(),
                                      key=lambda t: t[0][1])
        print(sorted_by_appereance)
        raise ValueError()
        sample.kmers_distribution = [kmer_ref[1]
                                     for kmer_ref in sorted_by_appereance]
        print(sample.kmers_distribution)
