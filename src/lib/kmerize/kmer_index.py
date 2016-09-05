import numpy as np
from collections import Counter
from typing import List

from lib.kmerize.sample import Sample
from lib.benchmarking import measure_time
from lib.ui import progress_bar
from lib.multiprocess import Pool
from lib.kmerize import rank


class KmerCountFunction:
    def __init__(self, k, queue):
        self.k = k
        self.queue = queue

    def __call__(self, sample_file: str):
        sample = Sample(sample_file)
        kmer_refs = np.concatenate(
            list(rank.count_kmer_ranks(seq, self.k)
                 for seq in sample.iter_seqs())
        )
        sample.kmer_index = Counter(kmer_refs)
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
