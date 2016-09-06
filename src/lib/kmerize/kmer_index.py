import numpy as np
from collections import Counter
from typing import List
from ctypes import cdll, POINTER, c_uint8, c_uint64, c_size_t, c_int


import src.lib.iof as iof
from src.lib.kmerize.sample import Sample
from src.lib.benchmarking import measure_time
from src.lib.ui import progress_bar
from src.lib.multiprocess import Pool
from src.lib.sparse import SparseArray

ranklib = cdll.LoadLibrary(iof.find_lib("src/lib/kmerize", "rank"))
ranklib.count_kmer_ranks.argtypes = [POINTER(c_uint8), POINTER(c_uint64),
                                     c_size_t, c_int]


class KmerCountFunction:
    def __init__(self, k, queue):
        self.k = k
        self.queue = queue

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

        self.queue.put(1)
        return sample


@measure_time(enabled=True)
def kmerize_samples(sample_files: List[str], k: int):
    packed_task = KmerCountFunction(k, Pool.instance().queue)
    result = Pool.instance().map_async(packed_task, sample_files)
    progress_bar(result, Pool.instance().queue, len(sample_files))

    samples = result.get()
    Pool.instance().clear()
    return dict([(sample.name, sample) for sample in samples])
