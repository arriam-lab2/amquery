#!/usr/bin/env python3

import os
import numpy as np
from typing import List, Callable, Mapping

from .src.lib import iof
from .src.lib.dist import kmerize_samples, LoadApply
from .src.lib.metrics import jaccard, generalized_jaccard, jsd, bray_curtis
from .src.lib.pwcomp import pwmatrix


distances = {'jaccard': jaccard, 'jsd': jsd, 'bc': bray_curtis,
             'gji': generalized_jaccard}


# TODO Replace this with the multiprocessing version from src.lib.pwcomp
def calc_distance_matrix(kmer_mapping: Mapping, k: int,
                         distance_func: Callable) -> (List[str], np.ndarray):

    labels = list(kmer_mapping.keys())
    func = LoadApply(distance_func)
    return labels, pwmatrix(func, kmer_mapping.values())


def make_kmer_data_mapping(config, input_dirs: str, k: int) -> dict:
    kmer_mapping = dict()
    for dirname in input_dirs:
        if not config.quiet:
            print("Processing ", dirname, "...")

        input_basename = (os.path.basename(os.path.split(dirname)[0]))
        kmer_output_dir = iof.make_sure_exists(
            os.path.join(config.working_directory, input_basename + ".kmers." +
                         str(k))
        )

        sample_files = [os.path.join(dirname, f)
                        for f in os.listdir(dirname)
                        if os.path.isfile(os.path.join(dirname, f))]

        kmer_mapping.update(kmerize_samples(sample_files, kmer_output_dir, k))

    return kmer_mapping


def run(config, input_dirs, kmer_size, distance):
    input_dirs = [iof.normalize(d) for d in input_dirs]
    #if config.force:
    #    iof.clear_dir(config.working_directory)

    kmer_mapping = make_kmer_data_mapping(config, input_dirs,
                                          kmer_size)

    distance_func = distances[distance]
    labels, pwmatrix = calc_distance_matrix(kmer_mapping, kmer_size,
                                            distance_func)

    out_path = os.path.join(config.working_directory,
                            distance + '_' + str(kmer_size) + '.txt')
    iof.write_distance_matrix(labels, pwmatrix, out_path)


if __name__ == "__main__":
    pass
