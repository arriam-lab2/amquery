#!/usr/bin/env python3

import os
from time import time
from typing import List, Callable, Mapping

import click
import numpy as np

from src.lib import iof
from src.lib.dist import kmerize_samples
from src.lib.metrics import jaccard, generalized_jaccard, jsd, bray_curtis
from src.lib.pwcomp import pwmatrix


# TODO Replace this with the multiprocessing version from src.lib.pwcomp
def calc_distance_matrix(samples: Mapping, k: int,
                         distance_func: Callable) -> (List[str], np.ndarray):

    tables = kmerize_samples(samples, k)
    labels = list(tables.keys())

    return labels, pwmatrix(distance_func, tables)

distances = {'jaccard': jaccard, 'jsd': jsd, 'bc': bray_curtis,
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
    if force:
        iof.clear_dir(out_dir)

    start = time()
    for f in fasta:
        if not quiet:
            click.echo("Processing "+f+"...")

        seqs = iof.load_seqs(f)
        distance_func = distances[distance]
        labels, dmatrix = calc_distance_matrix(seqs, kmer_size, distance_func)

        out_path = os.path.join(out_dir, os.path.splitext(
            os.path.basename(f))[0] + '.txt')
        iof.write_distance_matrix(labels, dmatrix, out_path)

    end = time()

    if not quiet:
        click.echo("Time: " + str(end-start))


if __name__ == "__main__":
    distance_matrix()
