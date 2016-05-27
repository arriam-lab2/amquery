#!/usr/bin/env python3

import os
import click
import pickle
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
        icoords = [pwmatrix[i, labels.index(x)] for x in coords]
        jcoords = [pwmatrix[j, labels.index(x)] for x in coords]
        list_coord.append((icoords, jcoords))

        wi = ulabels.index(pair[0])
        wj = ulabels.index(pair[1])
        list_wunifrac.append(wunifrac[wi, wj])
        list_uunifrac.append(uunifrac[wi, wj])

    output_dir = iof.normalize(output_dir)

    list_coord_output = os.path.join(output_dir, "list_coord.p")
    pickle.dump(list_coord, open(list_coord_output, "wb"))

    list_wunifrac_output = os.path.join(output_dir, "list_wunifrac.p")
    pickle.dump(list_wunifrac, open(list_wunifrac_output, "wb"))

    list_uunifrac_output = os.path.join(output_dir, "list_uunifrac.p")
    pickle.dump(list_uunifrac, open(list_uunifrac_output, "wb"))

    list_pairs_output = os.path.join(output_dir, "list_pairs.p")
    pickle.dump(pairs, open(list_pairs_output, "wb"))


if __name__ == "__main__":
    run()
