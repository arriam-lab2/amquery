#!/usr/bin/env python3


from typing import Iterable, Generator, Mapping
from collections import Counter
import multiprocessing as mp
import itertools
import zlib

from .work import N_JOBS


def kmerize_string(string: str, k: int, compression=9) -> Generator:
    byte_string = bytes(string, encoding="utf8")
    return (zlib.compress(byte_string[i:i+k], compression)
            for i in range(len(string)-k+1))


def count_kmers(strings: Iterable, k: int) -> Counter:
    return Counter(
        kmer for string in strings for kmer in kmerize_string(string, k))


def kmerize_samples(samples: Mapping, k: int) -> dict:
    batches = list(zip(samples.values(), itertools.repeat(k)))
    kmerised_seqs = workers.starmap(count_kmers, batches)
    return dict(zip(samples.keys(), kmerised_seqs))


if __name__ == "__main__":
    raise RuntimeError
else:
    workers = mp.Pool(processes=N_JOBS)
