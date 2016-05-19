#!/usr/bin/env python3


from typing import Generator, Iterable, Mapping
from collections import Counter
import zlib


def kmerize_string(string: str, k: int, compression: int=9) -> Generator[bytes]:
    byte_string = bytes(string, encoding="utf8")
    return (zlib.compress(byte_string[i:i+k], compression)
            for i in range(len(string)-k+1))


def count_kmers(strings: Iterable[str], k: int) -> Counter:
    return Counter(
        kmer for string in strings for kmer in kmerize_string(string, k))


def kmerize_samples(samples: Mapping[str, Iterable[str]],
                    k: int) -> Mapping[str, Counter]:
    return {sample: count_kmers(seqs, k) for sample, seqs in samples.items()}


if __name__ == "__main__":
    pass
