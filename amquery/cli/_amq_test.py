import click
import pandas as pd
from amquery.core.index import Index
from amquery.core.sample import Sample
from amquery.utils.config import Config


pass_config = click.make_pass_decorator(Config, ensure=True)
default_workon = './.amq/'

@click.group()
@click.option('--workon', default=default_workon, type=click.Path(),
              help='Index working directory')
@click.option('--force', '-f', is_flag=True,
              help='Force overwrite output directory')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
@click.option('--jobs', '-j', type=int, default=1,
              help='Number of jobs to start in parallel')
@pass_config
def cli(config, workon, force, quiet, jobs):
    config.load(workon)
    config.workon = workon if workon != default_workon else config.workon
    config.temp.force = force
    config.temp.quiet = quiet
    config.temp.jobs = jobs


import numpy as np

# load pairwise distance matrix from file
def load(input_filename: str):
    matrix = []
    with open(input_filename) as infile:
        labels = infile.readline()[:-1].split("\t")[1:]

        for line in infile.readlines():
            values = line[:-1].split("\t")[1:]
            matrix.append(values)

        matrix = [list(map(float, l)) for l in matrix]

    return pd.DataFrame(data=np.matrix(matrix), index=labels, columns=labels)


@cli.command()
@click.argument('input_files', type=click.Path(exists=True), nargs=-1, required=True)
@click.option('--reference', '-r', type=click.Path(exists=True), required=True)
@click.option('-k', type=int, required=True, help='Count of nearest neighbors')
@pass_config
def corr(config, input_files, reference, k):
    reference_df = load(reference)
    index = Index.load(config)

    for input_file in input_files:
        values, points = index.find(input_file, k)
        best_by_amq = [s.original_name.lower() for s in points]

        sample = Sample(input_file)
        best_by_reference = list(reference_df[sample.original_name].sort_values()[:k].index)

        print(sample.original_name)
        print(best_by_amq)
        print(best_by_reference)
        print()



