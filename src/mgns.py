#!/usr/bin/env python3

import click
import os
import pickle
from bunch import Bunch

import distance as mdist
import lib.prebuild as pre
import lib.iof as iof
import lib.vptree as vptree
from config import Config

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--workon', default='./.mgns/')
@click.option('--force', '-f', is_flag=True,
              help='Force overwrite output directory')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
@pass_config
def cli(config, workon, force, quiet):
    config.load(workon)
    config.temp.force = force
    config.temp.quiet = quiet


@cli.command()
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--single-file', '-f', is_flag=True,
              help='A single file containing reads for all samples')
@click.option('--kmer_size', '-k', type=int, help='K-mer size',
              default=50, required=True)
@click.option('--distance', '-d', type=click.Choice(mdist.distances.keys()),
              default='jsd', help='A distance metric')
@pass_config
def dist(config, input_dirs, single_file, kmer_size, distance):
    if "current_index" not in config:
        print("There is no index created. Run 'mgns init' or 'mgns use' first")
        return

    config.dist = Bunch()

    if single_file:
        input_file = input_dirs[0]
        input_dir = pre.split(config, input_file)
        input_dirs = [input_dir]
    else:
        input_dirs = [iof.normalize(d) for d in input_dirs]

    mdist.run(config, input_dirs, kmer_size, distance)
    config.save()


@cli.command()
@click.option('--pwmatrix', '-m', type=click.Path(exists=True),
              help='A distance matrix file')
@click.option('--coord-system', '-c', type=click.Path(exists=True),
              required=True)
@pass_config
def build(config: Config, pwmatrix: str, coord_system: str):
    pwmatrix_path = pwmatrix or config.get_pwmatrix_path()
    labels, pwmatrix = iof.read_distance_matrix(pwmatrix_path)
    cs_system = iof.read_coords(coord_system)
    vptree.dist(config, cs_system, labels, pwmatrix)
    config.save()


@cli.command()
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--single-file', '-f', is_flag=True,
              help='A single file containing reads for all samples')
@click.option('--max-samples', '-n', type=int,
              help='Max count of samples to analyze')
@click.option('--min', type=int, default=109,
              help='Minimum read length')
@click.option('--cut', type=int, default=208)
@click.option('--threshold', type=int, default=5000,
              help='Required read count per sample')
@pass_config
def filter(config, input_dirs, single_file, max_samples,
           min, cut, threshold):
    if config.temp.force:
        iof.clear_dir(config.workon)

    filtered_dirs = pre.filter_reads(config, input_dirs,
                                     min, None, cut, threshold)

    if max_samples:
        if single_file:
            raise NotImplementedError(
                "--single-file is not implemented yet")
        else:
            pre.rarefy(config, filtered_dirs, max_samples)


@cli.command()
@click.argument('name', type=str, required=True)
@pass_config
def init(config: Config, name: str):
    index_path = os.path.join(config.workon, name)
    iof.make_sure_exists(index_path)
    config.current_index = name
    config.save()


@cli.command()
@click.argument('name', type=str, required=True)
@pass_config
def use(config: Config, name: str):
    index_path = os.path.join(config.workon, name)
    if not iof.exists(index_path):
        print('No such index:', name)

    config.current_index = name
    config.save()


if __name__ == "__main__":
    pass
