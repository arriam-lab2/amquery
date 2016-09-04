import operator as op
import itertools
from collections import Counter
from typing import List, Mapping
from functools import reduce

from lib.kmerize.sample import Sample
from lib.benchmarking import measure_time
from lib.ui import progress_bar
from lib.multiprocess import Pool

from lib.kmerize import rank

acgt_alphabet = dict(zip([char for char in ('A', 'C', 'G', 'T')],
                         itertools.count()))


def _kmerize_string(string: str, k: int):
    return (string[i:i+k] for i in range(len(string)-k+1))


@measure_time(False)
def _lexicographic_rank(x: List, alphabet: Mapping) -> int:
    return rank.lexicographic_rank(x, alphabet)


def _isvalid(x: List, alphabet=acgt_alphabet):
    return reduce(op.and_, [char in alphabet for char in x])


class KmerCountFunction:
    def __init__(self, k, queue):
        self.k = k
        self.queue = queue

    def __call__(self, sample_file: str):
        sample = Sample(sample_file)
        kmer_refs = [_lexicographic_rank(kmer, acgt_alphabet)
                     for seq in sample.sequences() if _isvalid(seq)
                     for kmer in _kmerize_string(seq, self.k)]

        self.queue.put(1)

        sample.kmer_index = Counter(kmer_refs)
        return sample


@measure_time(enabled=True)
def kmerize_samples(sample_files: List[str], k: int):
    packed_task = KmerCountFunction(k, Pool.instance().queue)
    result = Pool.instance().map_async(packed_task, sample_files)
    progress_bar(result, Pool.instance().queue, len(sample_files))

    samples = result.get()
    Pool.instance().clear()
    return dict([(sample.name, sample) for sample in samples])
