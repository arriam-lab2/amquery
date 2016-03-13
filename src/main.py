#!/usr/bin/env python3

import itertools
import random
from collections import Counter

import iof
from metrics import jaccard, JSD
from subsample import *

def kmer_generator(string, k):
    kmer = string[:k]

    for i in range(len(string) - k):
        kmer = kmer[1:] + string[i + k]
        yield kmer


def kmer_counter(string_set, k):
    return Counter([kmer for string in string_set.values()
                         for kmer in kmer_generator(string, k)])


def fulldata_distance(seqs, k, distance_func):
    tables = {}
    for sample in seqs.keys():
        tables[sample] = kmer_counter(seqs[sample], k)

    result = [tables.keys()]
    for key1 in tables:
        values = [distance_func(tables[key1], tables[key2]) for key2 in tables]
        result.append([key1] + values)

    return result


if __name__ == "__main__":
    iof.clear_dir('out/ji')
    
    from time import time
    start = time()

    random.seed(42)
    k = 200
    jk_size = 100
    filename = 'data/seqs.fna'
    seqs = iof.load_seqs(filename)

    #dmatrix = fulldata_distance(seqs, k, jaccard)
    #iof.write_distance_matrix(dmatrix, 'out/ji_full.txt')

    dmatrix = fulldata_distance(seqs, k, JSD)
    iof.write_distance_matrix(dmatrix, 'out/jsd_full.txt')

    #import tempfile
    #for jk_result in jackknifed_distance(data, k, jk_size, jaccard):
    #    tfile = tempfile.NamedTemporaryFile(dir='./out/ji/', delete=False, prefix='ji_', suffix='.txt')
    #    iof.write_distance_matrix(jk_result, tfile.name)

    #for jk_result in jackknifed_distance(data, k, jk_size, JSD):
    #    tfile = tempfile.NamedTemporaryFile(dir='./out/jsd/', delete=False, prefix='jsd_', suffix='.txt')

    end = time()
    print("Time: " + str(end - start))


