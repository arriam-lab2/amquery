import operator as op
import itertools
from collections import Counter
from typing import List
from functools import reduce

from lib.benchmarking import measure_time

from lib.kmerize.sample import Sample

acgt_alphabet = dict(zip([char for char in ('A', 'C', 'G', 'T')],
                         itertools.count()))


def _kmerize_string(string: str, k: int):
    return (string[i:i+k] for i in range(len(string)-k+1))


@measure_time(False)
def _lexicographic_rank(x: List, alphabet=acgt_alphabet) -> int:
    return sum(alphabet[x[i]] * len(alphabet) ** (len(x) - i - 1)
               for i in range(len(x)))


def _isvalid(x: List, alphabet=acgt_alphabet):
    return reduce(op.and_, [char in alphabet for char in x])


def create_kmer_index(sample: Sample, k):
    kmer_refs = [_lexicographic_rank(kmer)
                 for seq in sample.sequences() if _isvalid(seq)
                 for kmer in _kmerize_string(seq, k)]

    return Counter(kmer_refs)
