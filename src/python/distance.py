#!/usr/bin/env python3

import click
import iof
import os

from collections import Counter
from time import time
from metrics import jaccard, generalized_jaccard, JSD, bray_curtis


def kmer_generator(string, k):
    kmer = string[1:k]

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
        result.append([key1] + values)

    return result


distances = {'jaccard': jaccard, 'jsd': JSD, 'bc': bray_curtis,
             'gji': generalized_jaccard}

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('fasta', type=click.Path(exists=True), nargs=-1, required=True)
@click.option('--kmer_size', '-k', type=int, help='K-mer size')
@click.option('--distance', '-d', type=click.Choice(distances.keys()),
              help='A distance metric')
@click.option('--out_dir', '-o', help='Output directory')
@click.option('--force', '-f', is_flag=True,
              help='Force overwrite output directory')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
def distance_matrix(fasta, kmer_size, distance, out_dir, force, quiet):

    iof.create_dir(out_dir)
    if (force):
        iof.clear_dir(out_dir)

    start = time()
    for f in fasta:
        if not quiet:
            click.echo("Processing " + f + "...")

        seqs = iof.load_seqs(f)
        distance_func = distances[distance]
        dmatrix = calc_distance_matrix(seqs, kmer_size, distance_func)

        out_path = os.path.join(out_dir, os.path.splitext(
            os.path.basename(f))[0] + '.txt')
        iof.write_distance_matrix(dmatrix, out_path)

    end = time()

    if not quiet:
        click.echo("Time: " + str(end - start))


if __name__ == "__main__":
    distance_matrix()
