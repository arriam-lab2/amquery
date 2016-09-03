import numpy as np
import operator as op
import itertools
from collections import Counter
from typing import List
from functools import reduce

from lib.kmerize.sample import Sample

acgt_alphabet = dict(zip([char for char in ('A', 'C', 'G', 'T')],
                         itertools.count()))


def _kmerize_string(string: str, k: int):
    return (string[i:i+k] for i in range(len(string)-k+1))


class LexicRankPrecalc:
    def __init__(self, kmer_size, alphabet=acgt_alphabet):
        n = len(alphabet)
        self.power = dict([(x, n ** x) for x in range(0, kmer_size)])

    def __getitem__(self, i):
        return self.power[i]


def _lexicographic_rank(x: List, precalc: LexicRankPrecalc, alphabet) -> int:
    return sum(alphabet[x[i]] * precalc[len(x) - i - 1]
               for i in range(len(x)))


def _isvalid(x: List, alphabet=acgt_alphabet):
    return reduce(op.and_, [char in alphabet for char in x])


def create_kmer_index(sample: Sample, k):
    print(sample.name)
    precalc = LexicRankPrecalc(k, acgt_alphabet)
    kmer_refs = [_lexicographic_rank(kmer, precalc, acgt_alphabet)
                 for seq in sample.sequences() if _isvalid(seq)
                 for kmer in _kmerize_string(seq, k)]

    return Counter(kmer_refs)
