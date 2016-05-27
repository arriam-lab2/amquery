#!/usr/bin/env python3

import click
import numpy as np
from typing import List

from src.lib import iof


def mean(input_dirs: List[str], output_file):
    files = iof.all_files(input_dirs)
    data = list(map(iof.read_distance_matrix, files))
    if len(data) == 0:
        raise ValueError("Empty input directories")

    labels = data[0][0]
    n = len(labels)
    mean = np.zeros((n, n), dtype=np.float)
    for _, table in data:
        mean += table

    mean /= n
    return labels, mean


@click.command()
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--output_file', '-o', help='Output file',
              required=True)
def run(input_dirs, output_file):
    input_dirs = [iof.normalize(d) for d in input_dirs]
    labels, pwmatrix = mean(input_dirs, output_file)
    iof.write_distance_matrix(labels, pwmatrix, output_file)

if __name__ == "__main__":
    run()
