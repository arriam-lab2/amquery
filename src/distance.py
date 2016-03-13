#!/usr/bin/env python3

import click
import iof

from collections import Counter
from time import time
from metrics import jaccard, JSD
from subsample import *


def kmer_generator(string, k):
    kmer = string[:k]

    for i in range(len(string) - k):
        kmer = kmer[1:] + string[i + k]
        yield kmer


def kmer_counter(string_set, k):
    return Counter([kmer for string in string_set
                         for kmer in kmer_generator(string, k)])


def kmerize(seqs, k):
    tables = {}

    for sample in seqs.keys():
        tables[sample] = kmer_counter(seqs[sample].values(), k)

    return tables


def calc_distance_matrix(seqs, k, distance_func):
    tables = kmerize(seqs, k) 
    result = [tables.keys()]

    for key1 in tables:
        values = [distance_func(tables[key1], tables[key2]) for key2 in tables]
        print(len(tables[key1]))
        result.append([key1] + values)

    return result


distances = {'jaccard': jaccard, 'jsd': JSD}


@click.command()
@click.option('--fasta', '-f', help='Input .fasta file')
@click.option('--kmer_size', '-k', type=int, help='K-mer size')
@click.option('--distance', '-d', type=click.Choice(distances.keys()), help='A distance metric')
@click.option('--out_dir', '-o', help='Output directory')
def distance_matrix(fasta, kmer_size, distance, out_dir):
 
    start = time()

    #iof.clear_dir('out/ji')
    seqs = iof.load_seqs(fasta)
    distance_func = distances[distance]
    dmatrix = calc_distance_matrix(seqs, kmer_size, distance_func)

    out_path = os.path.join(out_dir, os.path.splitext(os.path.basename(fasta))[0] + '.txt')
    iof.write_distance_matrix(dmatrix, out_path)

    end = time()
    click.echo("Time: " + str(end - start))


if __name__ == "__main__":
    distance_matrix()
