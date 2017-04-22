import numpy as np
import os.path
from collections import Counter
from typing import List
from ctypes import POINTER, c_uint8, c_uint64
from amquery.core.kmers_distr.sparse_array import SparseArray
from amquery.core.kmers_distr.lexrank import ranklib
from amquery.core.sample import Sample
from amquery.utils.benchmarking import measure_time
from amquery.utils.multiprocess import Pool
from amquery.utils.ui import progress_bar


class KmerCountFunction:
    def __init__(self, config, k, queue):
        self.config = config
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

    def rev_c(self, seq: np.array):
        z = np.array([3 - x for x in reversed(seq)])
        return z

    def __call__(self, sample_file: str):
        sample = Sample(sample_file)

        if os.path.exists(sample.make_kmer_index_obj_filename(self.config)):
            sample.load_kmer_index(self.config)
        else:
            kmer_ref_list = [np.concatenate([self._count_seq(seq), self._count_seq(self.rev_c(seq))])
                             for seq in sample.iter_seqs()]
            counter = Counter(np.concatenate(kmer_ref_list))
            cols = np.array(sorted(list(counter.keys())), dtype=np.uint64)
            data = np.array([counter[key] for key in cols], dtype=np.float)
            data /= np.sum(data)
            sample.set_kmer_index(SparseArray(cols, data))

        self.queue.put(1)
        return sample


@measure_time(enabled=True)
def kmerize_samples(config, sample_files: List[str], k: int):
    packed_task = KmerCountFunction(config, k, Pool.instance().queue)
    result = Pool.instance().map_async(packed_task, sample_files)
    if not config.temp.quiet:
        progress_bar(result, Pool.instance().queue, len(sample_files), 'Counting k-mers:')
    samples = result.get()
    Pool.instance().clear()
    return dict([(sample.name, sample) for sample in samples])
