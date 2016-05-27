#!/usr/bin/env python3

import click
import itertools
from typing import List

from src.lib import iof


def _check_labels(ulabels: List[str], wlabels: List[str],
                  coords: List[str]) -> List[str]:
    if not ulabels == wlabels:
        raise ValueError("Reordering columns not implemented yet")

    for label in coords:
        if label not in ulabels:
            raise ValueError("Inconsistent coord system: " + label)

    return ulabels


@click.command()
@click.option('--distance-matrix', '-d', type=click.Path(exists=True),
              required=True)
@click.option('--coord-system', '-i', type=click.Path(exists=True),
              required=True)
@click.option('--un-unifrac-file', '-u', type=click.Path(exists=True),
              required=True)
@click.option('--w-unifrac-file', '-w', type=click.Path(exists=True),
              required=True)
@click.option('--output_dir', '-o', required=True)
def run(distance_matrix, coord_system, un_unifrac_file,
        w_unifrac_file, output_dir):
    output_dir = iof.normalize(output_dir)

    labels, pwmatrix = iof.read_distance_matrix(distance_matrix)
    ulabels, uunifrac = iof.read_distance_matrix(un_unifrac_file)
    wlabels, wunifrac = iof.read_distance_matrix(w_unifrac_file)
    coords = iof.read_coords(coord_system)
    ulabels = _check_labels(ulabels, wlabels, coords)

    list_coord = []
    list_wunifrac = []
    list_uunifrac = []

    pairs = list(itertools.combinations(labels, 2))
    for pair in pairs:
        i = labels.index(pair[0])
        j = labels.index(pair[1])
        print(pair)
        print(pwmatrix[i, j])
        return

if __name__ == "__main__":
    run()
