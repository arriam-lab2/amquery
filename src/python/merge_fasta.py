#!/usr/bin/env python3

import click
import os
import os.path


def merge_fasta(dirlist, output_file):
    files = [os.path.join(dirname, f) for dirname in dirlist
             for f in os.listdir(dirname)
             if os.path.isfile(os.path.join(dirname, f))]

    with open(output_file, 'w') as outfile:
        for f in files:
            with open(f) as infile:
                print(f)
                for line in infile:
                    outfile.write(line)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command()
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--output_file', '-o', help='Output .fasta file',
              required=True)
def run(input_dirs, output_file):
    input_dirs = [os.path.join(x, '') for x in input_dirs]
    merge_fasta(input_dirs, output_file)


if __name__ == "__main__":
    run()
