#!/usr/bin/env python3

from subprocess import call
import os
from Bio import SeqIO
from collections import Counter
from typing import Mapping, List
import functools
import pickle

from .config import Config
from .iof import make_sure_exists


class SampleMap(dict):
    def register(self, config: Config, sample_files: List[str]):
        self.update(kmerize_samples(config, sample_files))
        return self

    @staticmethod
    def load(config: Config):
        try:
            with open(config.sample_map_path, 'rb') as f:
                sample_map = pickle.load(f)
        except IOError:
            sample_map = SampleMap()

        return sample_map

    def save(self, config):
        pickle.dump(self, open(config.sample_map_path, "wb"))

    @property
    def labels(self):
        return self.keys()

    @property
    def paths(self):
        return self.values()


class LoadApply:
    def __init__(self, func):
        self.func = func

    def __call__(self, x_kmer_file, y_kmer_file):
        xcounter = load_kmer_index(x_kmer_file)
        ycounter = load_kmer_index(y_kmer_file)
        return self.func(xcounter, ycounter)


def jellyfish_count(sample_file: str, kmer_size: int, tables_count: int,
                    hash_size: str, thread_num: int, output_file: str):
    call(["jellyfish", "count",
          "-C",
          "-m", str(kmer_size),
          "-c", str(tables_count),
          "-s", hash_size,
          "-t", str(thread_num),
          "-o", output_file,
          sample_file
          ])


def jellyfish_dump(index_file: str, output_file: str):
    call(["jellyfish", "dump",
          index_file,
          "-o", output_file
          ])


@functools.lru_cache(maxsize=32)
def load_kmer_index(counter_file: str) -> Counter:
    # print("Loading", counter_file)
    counter = Counter()
    seqs = SeqIO.parse(open(counter_file), "fasta")
    for seq_record in seqs:
        count, sequence = seq_record.id, str(seq_record.seq)
        counter[sequence] = int(count)

    return counter


def kmerize_samples(config: Config, sample_files: List[str]) -> Mapping:
    make_sure_exists(config.kmers_dir)

    mapping = dict()
    for sample_file in sample_files:
        shortname = os.path.split(sample_file)[1]
        sample_name, _ = os.path.splitext(shortname)
        output_jf_file = os.path.join(config.kmers_dir,
                                      sample_name + ".jf")

        if not os.path.exists(output_jf_file):
            jellyfish_count(sample_file,
                            config.dist.kmer_size,
                            config.jellyfish.tables_count,
                            config.jellyfish.hash_size,
                            config.temp.njobs,
                            output_jf_file)

        output_counter_file = os.path.join(config.kmers_dir,
                                           sample_name + ".counter")
        if not os.path.exists(output_counter_file):
            jellyfish_dump(output_jf_file, output_counter_file)

        mapping[sample_name] = output_counter_file

    return mapping


if __name__ == "__main__":
    pass
