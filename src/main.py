#!/usr/bin/env python3

import itertools
import random
from collections import Counter

import iof
from metrics import jaccard, JSD
from subsampling import *

def kmer_generator(string, k):
    kmer = string[:k]

    for i in range(len(string) - k):
        kmer = kmer[1:] + string[i + k]
        yield kmer


def hasher(string_set, k):
    table = {}
    for string in string_set:
        for kmer in kmer_generator(string, k):
            if kmer in table:
                table[kmer] = table[kmer] + 1
            else:
                table[kmer] = 1

    return table


def fulldata_distance(data, k, distance_func):
    tables = {}
    for sample in data.keys():
        tables[sample] = hasher(data[sample], k)

    result = [tables.keys()]
    for key1 in tables:
        table1 = tables[key1].copy()
        values = [distance_func(table1, tables[key2].copy()) for key2 in tables]
        result.append([key1] + values)

    return result


def jackknifed_distance(data, k, jk_size, distance_func):
    for subsample in jackknifed(data, jk_size):
        yield fulldata_distance(subsample, k, distance_func)


if __name__ == "__main__":
    iof.clear_dir('out/ji')
    
    from time import time
    start = time()

    random.seed(42)
    k = 200
    jk_size = 100
    filename = 'data/seqs.fna'
    data = iof.read_fasta(filename)

    dmatrix = fulldata_distance(data, k, jaccard)
    iof.write_distance_matrix(dmatrix, 'out/ji_full.txt')

    #dmatrix = fulldata_distance(data, k, JSD)
    #iof.write_distance_matrix(dmatrix, 'out/jsd_full.txt')

    #import tempfile
    #for jk_result in jackknifed_distance(data, k, jk_size, jaccard):
    #    tfile = tempfile.NamedTemporaryFile(dir='./out/ji/', delete=False, prefix='ji_', suffix='.txt')
    #    iof.write_distance_matrix(jk_result, tfile.name)

    #for jk_result in jackknifed_distance(data, k, jk_size, JSD):
    #    tfile = tempfile.NamedTemporaryFile(dir='./out/jsd/', delete=False, prefix='jsd_', suffix='.txt')

    end = time()
    print("Time: " + str(end - start))


