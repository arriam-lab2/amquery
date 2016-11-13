#!/usr/bin/env python3

import click
import os
import os.path


def merge_fasta(input_files, output_file):
    with open(output_file, 'w') as outfile:
        for f in input_files:
            with open(f) as infile:
                print(f)
                for line in infile:
                    outfile.write(line)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command()
@click.argument('input_files', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--output_file', '-o', help='Output .fasta file',
              required=True)
def run(input_files, output_file):
    merge_fasta(input_files, output_file)


if __name__ == "__main__":
    run()
