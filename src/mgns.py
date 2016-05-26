#!/usr/bin/env python3

import click
import os
import pickle
import python.distance as dist
import python.vptree as vptree
import python.testing as testing
import python.src.lib.prebuild as pre
import python.src.lib.iof as iof


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
@click.option('--distance', '-d', type=click.Choice(dist.distances.keys()),
              default='jsd', help='A distance metric')
@click.option('--test-size', type=float, default=0.0)
@pass_config
def build(config, input_dirs, single_file, kmer_size, distance, test_size):
    if single_file:
        input_file = input_dirs[0]
        input_dir = pre.split(config, input_file)
        input_dirs = [input_dir]
    else:
        input_dirs = [iof.normalize(d) for d in input_dirs]

    labels, pwmatrix = dist.run(config, input_dirs, kmer_size, distance)
    vptree.run(config, labels, pwmatrix, test_size)


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
@click.option('--tree-file', type=click.Path(),
              default='tree.pickle')
@click.option('--train-file', type=click.Path(),
              default='train.pickle')
@click.option('--unifrac-file', type=click.Path(),
              default='unifrac.txt')
@click.option('--dist-file', type=click.Path(),
              default='jsd_50.txt')
@click.option('-k', type=int)
@pass_config
def test(config, tree_file, train_file, unifrac_file, dist_file, k):
    tree_file = os.path.join(config.working_directory, tree_file)
    train_file = os.path.join(config.working_directory, train_file)
    unifrac_file = os.path.join(config.working_directory, unifrac_file)
    dist_file = os.path.join(config.working_directory, dist_file)

    labels, pwmatrix = iof.read_distance_matrix(dist_file)
    un_labels, unifrac = iof.read_distance_matrix(unifrac_file)
    tree = pickle.load(tree_file)
    train_labels = pickle.load(train_file)

    testing.run(config, labels, pwmatrix, un_labels, unifrac,
                tree, train_labels)


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
