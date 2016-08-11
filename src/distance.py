#!/usr/bin/env python3

import os
import numpy as np
from typing import List, Callable, Mapping

from lib import iof
from lib.dist import kmerize_samples, LoadApply
from lib.metrics import jaccard, generalized_jaccard, jsd, bray_curtis
from lib.pwcomp import PwMatrix, PairwiseDistance
from config import Config


distances = {'jaccard': jaccard, 'jsd': jsd, 'bc': bray_curtis,
             'gji': generalized_jaccard}


def calc_distance_matrix(kmer_mapping: Mapping[str, str], k: int,
                         distance_func: Callable) -> PwMatrix:

    labels = list(kmer_mapping.keys())
    func = LoadApply(distance_func)
    return PairwiseDistance.calculate(func, kmer_mapping)


def recalc_distance_matrix(kmer_mapping: Mapping[str, str], k: int,
                           distance_func: Callable,
                           pwmatrix: PwMatrix) -> PwMatrix:

    func = LoadApply(distance_func)
    return PairwiseDistance.append(func, pwmatrix, kmer_mapping.values())


def make_kmer_data_mapping(config: Config, input_dirs: str) -> dict:
    kmer_mapping = dict()
    kmer_size = config.dist.kmer_size
    for dirname in input_dirs:
        if not config.temp.quiet:
            print("Processing ", dirname, "...")

        kmer_output_dir = iof.make_sure_exists(
            os.path.join(config.workon, config.current_index,
                         "kmers." + str(kmer_size))
        )

        sample_files = [os.path.join(dirname, f)
                        for f in os.listdir(dirname)
                        if os.path.isfile(os.path.join(dirname, f))]

        kmer_mapping.update(kmerize_samples(sample_files, kmer_output_dir,
                                            kmer_size, config.temp.njobs))

    return kmer_mapping


def create(config: Config, input_dirs: List[str],
           kmer_size: int, distance: str):
    config.dist.func = distance
    config.dist.kmer_size = kmer_size

    input_dirs = [iof.normalize(d) for d in input_dirs]
    output_file = os.path.join(config.workon, config.current_index,
                               distance + '_' + str(kmer_size) + '.txt')

    if (not os.path.isfile(output_file)) or config.temp.force:
        kmer_mapping = make_kmer_data_mapping(config, input_dirs)

        distance_func = distances[distance]
        pwmatrix = calc_distance_matrix(kmer_mapping, kmer_size,
                                        distance_func)
        PairwiseDistance.save(pwmatrix, output_file)
    else:
        pwmatrix = PairwiseDistance.load(output_file)

    return pwmatrix


def add(config: Config, input_files: List[str]):
    kmer_size = config.dist.kmer_size
    print("OK go adding", input_files)
    kmer_output_dir = iof.make_sure_exists(
        os.path.join(config.workon, config.current_index,
                     "kmers." + str(kmer_size))
    )

    kmer_mapping = dict()
    kmer_mapping.update(kmerize_samples(input_files, kmer_output_dir,
                                        kmer_size, config.temp.njobs))

    print("Got data mapping:")
    print(kmer_mapping)
    distance_func = distances[config.dist.func]
    pwmatrix_file = os.path.join(config.workon, config.current_index,
                                 config.dist.func + '_' + str(kmer_size) +
                                 '.txt')

    pwmatrix = PairwiseDistance.load(pwmatrix_file)

    print("OLD pwmatrix:")
    print(labels)
    print(pwmatrix)
    pwmatrix = recalc_distance_matrix(kmer_mapping, kmer_size,
                                      distance_func, pwmatrix)

    print("NEW pwmatrix:")
    print(labels)
    print(pwmatrix)
    return labels, pwmatrix

if __name__ == "__main__":
    pass
