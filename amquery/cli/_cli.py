#!/usr/bin/env python3

import click
import os
from bunch import Bunch
from typing import List

import amquery.utils.iof as iof
from amquery.utils.config import Config
from amquery.core.distance import distances
from amquery.core import Index


pass_config = click.make_pass_decorator(Config, ensure=True)


def _index_check(config: Config):
    message = "There is no index created. Run 'amq init' or 'amq use' first"
    assert "current_index" in config, message
    assert iof.exists(config.index_path), message


def _build_check(config: Config):
    if config.built.lower() != "true":
        raise ValueError("First you have to build the index. Run 'amq build'")


@click.group()
@click.option('--workon', default='./.amq/', type=click.Path(),
              help='Index working directory')
@click.option('--force', '-f', is_flag=True,
              help='Force overwrite output directory')
@click.option('--quiet', '-q', is_flag=True, help='Be quiet')
@click.option('--jobs', '-j', type=int, default=1,
              help='Number of jobs to start in parallel')
@pass_config
def cli(config: Config, workon: str, force: bool,
        quiet: bool, jobs: int):
    config.load(workon)
    config.workon = workon
    config.temp.force = force
    config.temp.quiet = quiet
    config.temp.jobs = jobs


@cli.command()
@click.argument('name', type=str, required=True)
@pass_config
def init(config: Config, name: str):
    index_path = os.path.join(config.workon, name)
    iof.make_sure_exists(index_path)
    config.current_index = name

    config.built = "false"
    config.save()


@cli.command()
@click.argument('input_files', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--kmer_size', '-k', type=int, help='K-mer size',
              default=15)
@click.option('--distance', '-d', type=click.Choice(distances.keys()),
              default='jsd', help='A distance metric')
@pass_config
def build(config: Config, kmer_size: int, distance: str, input_files: List[str]):
    _index_check(config)

    config.dist = Bunch()
    config.dist.func = distance
    config.dist.kmer_size = kmer_size

    index = Index.build(config, input_files)
    index.save()

    config.built = "true"
    config.save()


@cli.command()
@click.option('--kmer_size', '-k', type=int, help='K-mer size',
              default=15)
@click.option('--distance', '-d', type=click.Choice(distances.keys()),
              default='jsd', help='A distance metric')
@pass_config
def refine(config: Config, kmer_size: int, distance: str):
    _index_check(config)

    config.dist = Bunch()
    config.dist.func = distance
    config.dist.kmer_size = kmer_size

    index = Index.load(config)
    index.refine()
    index.save()

    config.built = "true"
    config.save()


@cli.command()
@click.argument('input_files', type=click.Path(exists=True), nargs=-1,
                required=True)
@pass_config
def add(config: Config, input_files: List[str]):
    _index_check(config)

    index = Index.load(config)
    index.add(input_files)
    index.save()


@cli.command()
@click.argument('name', type=str, required=True)
@pass_config
def use(config: Config, name: str):
    index_path = os.path.join(config.workon, name)
    if not iof.exists(index_path):
        print('No such index:', name)

    config.current_index = name
    config.save()


@cli.command()
@pass_config
def stats(config: Config):
    _index_check(config)
    _build_check(config)

    index = Index.load(config)
    indexed = len(index.sample_map)

    print("Current index:", config.current_index)
    print("Indexed:", indexed, "samples")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True),
                required=True)
@click.option('-k', type=int, required=True,
              help='Count of nearest neighbors')
@pass_config
def find(config: Config, input_file: str, k: int):
    _index_check(config)
    _build_check(config)

    index = Index.load(config)
    values, points = index.find(input_file, k)
    print(k, "nearest neighbors:")
    print('\t'.join(x for x in ['Hash', 'Sample', 'Similarity']))
    print('\n'.join('\t'.join(str(x) for x in [sample.name[:6], sample.original_name, value]) \
                    for value, sample in zip(values, points)))
