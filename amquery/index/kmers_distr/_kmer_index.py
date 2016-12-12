import numpy as np
from collections import Counter
from typing import List
from ctypes import cdll, POINTER, c_uint8, c_uint64, c_size_t, c_int
import os
import itertools

from ._sparse import SparseArray
from ..sample import Sample

import amquery.utils.iof as iof
from amquery.utils.benchmarking import measure_time

ranklib = None


class KmerCountFunction:

    def __init__(self, k):
        self.k = k

    def _count_seq(self, seq: np.array):
        if seq.size > 0 and seq.size >= self.k:
            ranks = np.zeros(len(seq) - self.k + 1, dtype=np.uint64)
            seq_pointer = seq.ctypes.data_as(POINTER(c_uint8))
            ranks_pointer = ranks.ctypes.data_as(POINTER(c_uint64))
            ranklib.count_kmer_ranks(seq_pointer, ranks_pointer,
                                     len(seq), self.k)
            return ranks
        else:
            return seq

    def __call__(self, sample_file: str):
        sample = Sample(sample_file)
        kmer_refs = np.concatenate(
            list(self._count_seq(seq) for seq in sample.iter_seqs())
        )

        counter = Counter(kmer_refs)
        cols = np.array(sorted(list(counter.keys())), dtype=np.uint64)
        data = np.array([counter[key] for key in cols], dtype=np.float)
        data /= np.sum(data)
        sample.kmer_index = SparseArray(cols, data)

        return sample


@measure_time(enabled=True)
def kmerize_samples(sample_files: List[str], k: int):
    packed_task = KmerCountFunction(k)
    samples = map(packed_task, sample_files)
    return dict([(sample.name, sample) for sample in samples])


if __name__ == "__main__":
    raise RuntimeError()
else:
    libdir = os.path.dirname(os.path.abspath(__file__))
    ranklib = cdll.LoadLibrary(iof.find_lib(libdir, "rank"))
    ranklib.count_kmer_ranks.argtypes = [POINTER(c_uint8), POINTER(c_uint64),
                                         c_size_t, c_int]
