import functools
import os
from Bio import SeqIO
from collections import Counter
from typing import Callable, List, Mapping

from .iof import make_sure_exists
from .config import Config


class LoadApply:
    def __init__(self, func: Callable):
        self.func = func

    def __call__(self, x_kmer_file: str, y_kmer_file: str):
        xcounter = LoadApply._load_kmer_index(x_kmer_file)
        ycounter = LoadApply._load_kmer_index(y_kmer_file)
        return self.func(xcounter, ycounter)

    @staticmethod
    @functools.lru_cache(maxsize=32)
    def _load_kmer_index(counter_file: str) -> Counter:
        counter = Counter()
        seqs = SeqIO.parse(open(counter_file), "fasta")
        for seq_record in seqs:
            count, sequence = seq_record.id, str(seq_record.seq)
            counter[sequence] = int(count)

        return counter


class KmerCounter:
    @staticmethod
    def kmerize_samples(config: Config, sample_files: List[str]) -> Mapping:
        make_sure_exists(config.kmers_dir)

        mapping = dict()
        for sample_file in sample_files:
            shortname = os.path.split(sample_file)[1]
            sample_name, _ = os.path.splitext(shortname)
            output_jf_file = os.path.join(config.kmers_dir,
                                          sample_name + ".jf")

            if not os.path.exists(output_jf_file):
                KmerCounter._count(sample_file,
                       config.dist.kmer_size,
                       config.jellyfish.tables_count,
                       config.jellyfish.hash_size,
                       config.temp.njobs,
                       output_jf_file)

            output_counter_file = os.path.join(config.kmers_dir,
                                               sample_name + ".counter")
            if not os.path.exists(output_counter_file):
                KmerCounter._dump(output_jf_file, output_counter_file)

            mapping[sample_name] = output_counter_file

        return mapping


    @staticmethod
    def _count(sample_file: str,
               kmer_size: int, tables_count: int,
               hash_size: str, thread_num: int,
               output_file: str):

        call(["jellyfish", "count",
              "-C",
              "-m", str(kmer_size),
              "-c", str(tables_count),
              "-s", hash_size,
              "-t", str(thread_num),
              "-o", output_file,
              sample_file
              ])

    @staticmethod
    def _dump(index_file: str, output_file: str):
        call(["jellyfish", "dump",
              index_file,
              "-o", output_file
              ])
