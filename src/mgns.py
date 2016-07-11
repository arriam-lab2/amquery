#!/usr/bin/env python3

import click
import os
import pickle
import testing
import distance as mdist
import src.lib.prebuild as pre
import src.lib.iof as iof
import src.lib.vptree as vptree


class Config(object):
    def __init__(self):
        pass

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--working-directory', default='./mgns_out/')
@click.option('--force', '-f', is_flag=True,
              help='Force overwrite output directory')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
@pass_config
def cli(config, working_directory, force, quiet):
    config.working_directory = iof.make_sure_exists(working_directory)
    config.force = force
    config.quiet = quiet


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
    if single_file:
        input_file = input_dirs[0]
        input_dir = pre.split(config, input_file)
        input_dirs = [input_dir]
    else:
        input_dirs = [iof.normalize(d) for d in input_dirs]

    mdist.run(config, input_dirs, kmer_size, distance)


@cli.command()
@click.option('--pwmatrix', '-m', type=click.Path(exists=True),
              help='A distance matrix file', required=True)
@click.option('--test-size', type=float, default=0.0)
@click.option('--coord-system', '-c', type=click.Path(exists=True),
              required=True)
@click.option('--distance', '-d', type=click.Choice(mdist.distances.keys()),
              default='jsd', help='A distance metric')
@pass_config
def build(config, pwmatrix, test_size, coord_system, distance):
    input_file = pwmatrix
    labels, pwmatrix = iof.read_distance_matrix(input_file)
    cs_system = iof.read_coords(coord_system)
    vptree.dist(config, labels, pwmatrix, test_size, distance)
    vptree.csdist(config, cs_system, labels, pwmatrix,
                  test_size, 'cs_' + distance)


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
    if config.force:
        iof.clear_dir(config.working_directory)

    filtered_dirs = pre.filter_reads(config, input_dirs,
                                     min, None, cut, threshold)

    if max_samples:
        if single_file:
            raise NotImplementedError(
                "--single-file is not implemented yet")
        else:
            pre.rarefy(config, filtered_dirs, max_samples)


@cli.command()
@click.option('--dist', '-d', type=click.Choice(mdist.distances.keys()),
              default='jsd')
@click.option('--unifrac-file', '-f', type=click.Path(exists=True),
              required=True)
@pass_config
def test(config, dist, unifrac_file):
    dist_tree_file = os.path.join(config.working_directory,
                                  dist + '_tree.p')
    dist_train_file = os.path.join(config.working_directory,
                                   dist + '_train.p')

    with open(dist_tree_file, 'rb') as treef:
        dist_tree = pickle.load(treef)

    with open(dist_train_file, 'rb') as trainf:
        train_labels = pickle.load(trainf)

    cs_tree_file = os.path.join(config.working_directory,
                                'cs_' + dist + '_tree.p')
    cs_train_file = os.path.join(config.working_directory,
                                 'cs_' + dist + '_train.p')

    with open(cs_tree_file, 'rb') as treef:
        cs_tree = pickle.load(treef)

    with open(cs_train_file, 'rb') as trainf:
        cs_train_labels = pickle.load(trainf)

    labels, pwmatrix = iof.read_distance_matrix(unifrac_file)
    k_values = range(3, len(train_labels))

    testing.dist(config, dist_tree, train_labels, labels,
                 pwmatrix, k_values, 'dist.txt')
    testing.dist(config, cs_tree, cs_train_labels,
                 labels, pwmatrix, k_values, 'cs_dist.txt')
    testing.baseline(config, dist_tree, train_labels,
                     labels, pwmatrix, k_values)


@cli.command()
@pass_config
def learn(config):
    # TODO:
    # 1. make sure there is proper qiime output files
    # 2. make sure there is a pwmatrix file
    # 3. run a network

    raise NotImplementedError("Not implemented yet")


@cli.command()
@pass_config
def search(config):
    # TODO:
    # 1. make sure there is a pwmatrix file (result of nns build)
    # 2. make sure there is a result from nns learn (k value)
    # 2. run vptree.py (search)
    raise NotImplementedError("Not implemented yet")


@cli.command()
@pass_config
def stats(config):
    # TODO:
    # parse arguments, run length/count.py
    raise NotImplementedError("Not implemented yet")


if __name__ == "__main__":
    pass
