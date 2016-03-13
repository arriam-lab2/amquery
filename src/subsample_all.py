#!/usr/bin/env python3

import subsample
import click
import biom
import iof
import os
from os import path


@click.command()
@click.option('--input_dir', '-i', help='Input directory containing OTU tables in biom format')
@click.option('--fasta', '-f', help='Input .fasta file')
@click.option('--seqs_otus', '-s', help='Input file mapping OTUs to the sequences')
@click.option('--out_dir', '-o', help='Output directory')
def subsample_all(input_dir, fasta, seqs_otus, out_dir):
    seqs = iof.load_seqs(fasta)
    so_map = subsample.load_seqs_otus_map(seqs_otus)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    x = os.listdir(input_dir)
    names = [name for name in x if os.path.isfile(os.path.join(input_dir, name))]
    for name in names:
        path = os.path.join(input_dir, name)
        biom_table = biom.load_table(path)
        out_path = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + '.fna')
        subsample.do_subsample(biom_table, seqs, so_map, out_path)

if __name__ == "__main__":
    subsample_all()


