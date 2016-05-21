#!/usr/bin/env python3

import click
import python.distance as dist
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
@pass_config
def build(config, input_dirs, single_file,
          kmer_size, distance):

    # TODO:
    # 1. prebuild:
    #   1.1 split fasta file if neccessary
    #   1.2 merge fasta files if neccesary
    #   1.3 read_filter.py
    #
    # 2. make a pwmatrix file (distance.py)
    # 3. build a tree (vptree.py build)

    if single_file:
        pass
    else:
        pre.prebuild(config, input_dirs, single_file)

    dist.run(config, input_dirs, kmer_size, distance)


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
