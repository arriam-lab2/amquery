#!/usr/bin/env python3

import os
from time import time
from typing import List, Callable, Mapping

import click
import numpy as np

from src.lib import iof
from src.lib.dist import kmerize_samples, LoadApply
from src.lib.metrics import jaccard, generalized_jaccard, jsd, bray_curtis
from src.lib.pwcomp import pwmatrix


# TODO Replace this with the multiprocessing version from src.lib.pwcomp
def calc_distance_matrix(kmer_mapping: Mapping, k: int,
                         distance_func: Callable) -> (List[str], np.ndarray):

    labels = list(kmer_mapping.keys())
    func = LoadApply(distance_func)
    return labels, pwmatrix(func, kmer_mapping.values())


def make_kmer_data_mapping(input_dirs: str, output_dir: str,
                           k: int, quiet: bool) -> dict:

    kmer_mapping = dict()
    for dirname in input_dirs:
        if not quiet:
            print("Processing", dirname, "...")

        input_basename = (os.path.basename(os.path.split(dirname)[0]))
        kmer_output_dir = os.path.join(output_dir,
                                       input_basename + ".kmers." +
                                       str(k))
        iof.create_dir(kmer_output_dir)

        sample_files = [os.path.join(dirname, f)
                        for f in os.listdir(dirname)
                        if os.path.isfile(os.path.join(dirname, f))]

        kmer_mapping.update(kmerize_samples(sample_files, kmer_output_dir, k))

    return kmer_mapping


def pathnames_check(input_dirs, output_dir, force):
    input_dirs = [os.path.join(x, '') for x in input_dirs]
    output_dir = os.path.join(output_dir, '')
    iof.create_dir(output_dir)
    if force:
        iof.clear_dir(output_dir)

    return input_dirs, output_dir

distances = {'jaccard': jaccard, 'jsd': jsd, 'bc': bray_curtis,
             'gji': generalized_jaccard}

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--kmer_size', '-k', type=int, help='K-mer size',
              required=True)
@click.option('--distance', '-d', type=click.Choice(distances.keys()),
              help='A distance metric')
@click.option('--output_dir', '-o', help='Output directory',
              required=True)
@click.option('--force', '-f', is_flag=True,
              help='Force overwrite output directory')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
def distance_matrix(input_dirs, kmer_size, distance, output_dir, force, quiet):
    start = time()
    input_dirs, output_dir = pathnames_check(input_dirs, output_dir, force)

    kmer_mapping = make_kmer_data_mapping(input_dirs, output_dir,
                                          kmer_size, quiet)

    distance_func = distances[distance]
    labels, pwmatrix = calc_distance_matrix(kmer_mapping, kmer_size, distance_func)

    out_path = os.path.join(output_dir, distance, '_', kmer_size, '.txt')
    iof.write_distance_matrix(labels, pwmatrix, out_path)

    end = time()

    if not quiet:
        click.echo("Time: " + str(end-start))


if __name__ == "__main__":
    distance_matrix()
