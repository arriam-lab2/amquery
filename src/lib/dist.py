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


class SampleMap(Mapping):
    def __init__(self, config: Config):
        self.mapping = dict()
        self.config = config

    @staticmethod
    def kmerize(config: Config, sample_files: List[str]):
        sample_map = SampleMap(config)
        sample_map.mapping = dict()
        kmer_size = config.dist.kmer_size

        sample_map.mapping = kmerize_samples(sample_files,
                                             config.get_kmers_dir(),
                                             kmer_size,
                                             config.temp.njobs)
        return sample_map


    @staticmethod
    def load(config: Config):
        try:
            with open(config.get_sample_map_path(), 'rb') as f:
                sample_map = pickle.load(f)
        except IOError:
            sample_map = SampleMap(config)

        return sample_map

    def save(self):
        pickle.dump(self, open(self.config.get_sample_map_path(), "wb"))

    def __getitem__(self, sample_name: str) -> str:
        return self.mapping[sample_name]

    def __setitem__(self, key, value):
        self.mapping[key] = value

    def __len__(self):
        return self.mapping.len

    def items(self):
        return self.mapping.items()

    def update(self, other=None, **kwargs):
        if other is not None:
            for k, v in other.items() if isinstance(other, Mapping) else other:
                self[k] = v

        for k, v in kwargs.items():
            self[k] = v

    def labels(self):
        return self.mapping.keys()

    def paths(self):
        return self.mapping.values()


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


def kmerize_samples(sample_files: list, tempdir: str,
                    kmer_size: int, njobs: int) -> Mapping:

    mapping = dict()
    for sample_file in sample_files:
        shortname = os.path.split(sample_file)[1]
        sample_name, _ = os.path.splitext(shortname)
        output_jf_file = os.path.join(tempdir, sample_name + ".jf")

        if not os.path.exists(output_jf_file):
            # Jellyfish count
            tables_count = 10
            hash_size = "100M"
            thread_num = njobs
            jellyfish_count(sample_file, kmer_size, tables_count, hash_size,
                            thread_num, output_jf_file)

        output_counter_file = os.path.join(tempdir, sample_name + ".counter")
        if not os.path.exists(output_counter_file):
            # Jellyfish dump
            jellyfish_dump(output_jf_file, output_counter_file)

        mapping[sample_name] = output_counter_file

    return mapping


if __name__ == "__main__":
    pass
