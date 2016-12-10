#!/usr/bin/env python3

import click
import os
import os.path
import collections
from Bio import SeqIO

def length(input_file: str):
    with open(input_file, 'r') as infile:
        seqs = list(SeqIO.parse(infile, "fasta"))
        return len(seqs)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command()
@click.argument('input_files', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--depth', required=True)
def run(input_files, depth):
    for input_file in input_files:
        if length(input_file) < depth:
            os.remove(input_file)


if __name__ == "__main__":
    run()