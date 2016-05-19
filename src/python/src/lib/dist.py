#!/usr/bin/env python3

import os
from collections import Counter
from time import time
import zlib


def kmerize_string(string, k, compress=9):
    byte_string = bytes(string, encoding="utf8")
    return (zlib.compress(byte_string[i:i+k], compress)
            for i in range(len(string)-k+1))


def count_kmers(strings, k):
    return Counter(
        kmer for string in strings for kmer in kmerize_string(string, k))


def kmerize_samples(seqs, k):
    return {sample: count_kmers(seqs[sample].values(), k) for sample in seqs}


if __name__ == "__main__":
    pass
