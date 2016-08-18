import os
from subprocess import call
from typing import Callable, List, Mapping

from lib.iof import make_sure_exists
from lib.config import Config
from lib.kmerize.sample import Sample, get_sample_name


class KmerCounter:

    @staticmethod
    def kmerize(config: Config, sample_file: str):
        make_sure_exists(config.kmers_dir)

        sample_name = get_sample_name(sample_file)
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

        return Sample(sample_name, sample_file, output_counter_file)


    @staticmethod
    def kmerize_samples(config: Config,
                        sample_files: List[str]) -> Mapping[str, str]:

        result = dict()
        for sample_file in sample_files:
            sample_name = get_sample_name(sample_file)
            result[sample_name] = KmerCounter.kmerize(config, sample_file)

        return result

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
