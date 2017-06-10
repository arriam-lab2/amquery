import numpy as np
from collections import Counter
from ctypes import POINTER, c_uint8, c_uint64
from typing import List
from amquery.core.preprocessing.kmer_counter.lexrank import ranklib
from amquery.core.distance.kmers_distr.sparse_array import SparseArray
from amquery.utils.benchmarking import measure_time
from amquery.utils.multiprocess import Pool
from amquery.utils.ui import progress_bar
from amquery.core.preprocessing import Preprocessor


class KmerCounter(Preprocessor):
    def __init__(self, k):
        self.k = k

    def _count_seq(self, seq):
        if seq.size > 0 and seq.size >= self.k:
            ranks = np.zeros(len(seq) - self.k + 1, dtype=np.uint64)
            seq_pointer = seq.ctypes.data_as(POINTER(c_uint8))
            ranks_pointer = ranks.ctypes.data_as(POINTER(c_uint64))
            ranklib.count_kmer_ranks(seq_pointer, ranks_pointer,
                                     len(seq), self.k)
            return ranks
        else:
            return seq

    def __call__(self, sample):
        """
        :param sample: Sample
        :return: Sample
        """
        kmer_refs = np.concatenate(list(self._count_seq(seq) for seq in sample.iter_seqs()))
        counter = Counter(kmer_refs)
        cols = np.array(sorted(list(counter.keys())), dtype=np.uint64)
        data = np.array([counter[key] for key in cols], dtype=np.float)
        data /= np.sum(data)
        sample.set_kmer_index(SparseArray(cols, data))
        return sample


@measure_time(enabled=True)
def kmerize_samples(sample_files: List[str], k: int):
    packed_task = KmerCountFunction(k, Pool.instance().queue)
    result = Pool.instance().map_async(packed_task, sample_files)
    progress_bar(result, Pool.instance().queue, len(sample_files), 'Counting k-mers:')

    samples = result.get()
    Pool.instance().clear()
    return dict([(sample.name, sample) for sample in samples])
