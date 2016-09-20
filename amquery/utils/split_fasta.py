#!/usr/bin/env python3

import click
import os
import os.path
import collections
from Bio import SeqIO

from amquery.utils.iof import make_sure_exists


# Split a fasta by sample names
def split_fasta(input_file: str, output_dir: str):
    print("Splitting", input_file)
    read_mapping = collections.defaultdict(list)
    with open(input_file, 'r') as infile:
        for seq_record in SeqIO.parse(infile, "fasta"):
            sample_name = seq_record.id.split(" ")[0]
            sample_name = sample_name.split("_")[0]
            read_mapping[sample_name].append(seq_record)

    # creating a folder for splitted files
    output_dir = os.path.join(output_dir, "splitted")
    output_dir = make_sure_exists(output_dir)

    # writing splitted files
    for sample in read_mapping.keys():
        output_file = os.path.join(output_dir,
                                   sample + ".fasta")
        SeqIO.write(read_mapping[sample], output_file, "fasta")

    return output_dir


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command()
@click.argument('input_files', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--output_dir', '-o', help='Output directory',
              required=True)
def run(input_files, output_dir):
    for input_file in input_files:
        split_fasta(input_file, output_dir)


if __name__ == "__main__":
    run()
