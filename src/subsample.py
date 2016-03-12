#!/usr/bin/env python3

import random
import biom
import iof
import click
import os
from collections import defaultdict

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
        read_map = zip(biom_table.ids(), biom_table.data(obs, axis="observation").astype(int))

        for cls, count in read_map:
            reads.extend(random.sample(so_map[obs][cls], count))

    with open(out_path, 'w') as f:
        s = '\n'.join('>' + x + '\n' + seqs[get_class(x)][x] for x in reads)
        f.write(s)


@click.command()
@click.option('--input_path', '-i', help='Input (rarefied) OTU table in biom format')
@click.option('--fasta', '-f', help='Input .fasta file')
@click.option('--seqs_otus', '-s', help='Input file mapping OTUs to the sequences')
@click.option('--out_dir', '-o', help='Output directory')
def subsample(input_path, fasta, seqs_otus, out_dir):
    biom_table = biom.load_table(input_path)
    seqs = iof.load_seqs(fasta)
    so_map = load_seqs_otus_map(seqs_otus)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_path = os.path.join(out_dir, os.path.splitext(os.path.basename(input_path))[0] + '.txt')
    do_subsample(biom_table, seqs, so_map, out_path)


if __name__ == "__main__":
    subsample()


