#!/usr/bin/env python3

import os
import random
from collections import defaultdict

import biom
import click

from src.lib import iof


def get_class(read_id):
    return read_id.split('_')[0]


def load_seqs_otus_map(filename):
    so_map = {}
    lines = [line.rstrip('\n') for line in open(filename)]
    for line in lines:
        items = line.split('\t')
        so_map[items[0]] = items[1:]

    for otu in so_map:
        d = defaultdict(list)
        for value in so_map[otu]:
            d[get_class(value)].append(value)

        so_map[otu] = d

    return so_map


def do_subsample(biom_table, seqs, so_map, out_path):
    ids = biom_table.ids(axis="observation")
    reads = []
    for obs in ids:
        read_map = zip(biom_table.ids(), biom_table.data(
            obs, axis="observation").astype(int))

        for cls, count in read_map:
            reads.extend(random.sample(so_map[obs][cls], count))

    with open(out_path, 'w') as f:
        s = '\n'.join('>' + x + '\n' + seqs[get_class(x)][x] for x in reads)
        f.write(s)


@click.command()
@click.argument('biom_files', type=click.Path(exists=True), nargs=-1)
@click.option('--fasta', '-f', help='Input .fasta file')
@click.option('--seqs_otus', '-s',
              help='Input file mapping OTUs to the sequences')
@click.option('--out_dir', '-o', help='Output directory')
def subsample(biom_files, fasta, seqs_otus, out_dir):
    for biomf in biom_files:
        click.echo("Processing " + biomf + "...")
        biom_table = biom.load_table(biomf)
        seqs = iof.load_seqs(fasta)
        so_map = load_seqs_otus_map(seqs_otus)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        out_path = os.path.join(out_dir, os.path.splitext(
            os.path.basename(biomf))[0] + '.fna')
        do_subsample(biom_table, seqs, so_map, out_path)


if __name__ == "__main__":
    subsample()
