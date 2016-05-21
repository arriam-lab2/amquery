#!/usr/bin/env python3

import click
import python.distance as dist


@click.group()
def cli():
    pass


@cli.command()
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--single-file', '-f', is_flag=True,
              help='A single file containing reads for all samples')
@click.option('--kmer_size', '-k', type=int, help='K-mer size',
              default=50, required=True)
@click.option('--distance', '-d', type=click.Choice(dist.distances.keys()),
              default='jsd', help='A distance metric')
@click.option('--output_dir', '-o', help='Output directory',
              default='./nns_output/', required=True)
@click.option('--force', '-f', is_flag=True,
              help='Force overwrite output directory')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
def build(input_dirs, kmer_size, distance, output_dir, force, quiet):

    # TODO:
    # 1. prepare reads:
    #   1.1 split fasta file if neccessary
    #   1.2 merge fasta files if neccesary
    #   1.3 read_filter.py
    #
    # 2. make a pwmatrix file (distance.py)
    # 3. build a tree (vptree.py build)

    dist.run(input_dirs, kmer_size, distance, output_dir, force, quiet)


@cli.command()
def learn():
    # TODO:
    # 1. make sure there is proper qiime output files
    # 2. make sure there is a pwmatrix file
    # 3. run a network

    raise NotImplementedError("Not implemented yet")


@cli.command()
def search():
    # TODO:
    # 1. make sure there is a pwmatrix file (result of nns build)
    # 2. make sure there is a result from nns learn (k value)
    # 2. run vptree.py (search)
    raise NotImplementedError("Not implemented yet")


@cli.command()
def stats():
    # TODO:
    # parse arguments, run length/count.py
    raise NotImplementedError("Not implemented yet")


if __name__ == "__main__":
    pass
