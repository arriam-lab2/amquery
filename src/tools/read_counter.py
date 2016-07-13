#!/usr/bin/env python3

import click
from Bio import SeqIO
import os
import os.path
import iof
import matplotlib.pyplot as plt


# Counting reads for a .fasta/fastq file
def read_count(filename):
    name, extension = os.path.splitext(filename)
    extension = extension[1:]

    count = 0
    for _ in SeqIO.parse(filename, extension):
        count += 1

    return count


def plot(count_stats, plot_output_file):
    plt.hist(count_stats, normed=1, facecolor='green', alpha=0.5)
    plt.xlabel('Read count')
    plt.ylabel('Number of samples')
    plt.title('Distribution of read count')

    plt.subplots_adjust(left=0.15)
    # plt.show()
    plt.savefig(plot_output_file)


def run_for_dirlist(dirlist, txt_output_file, plot_output_file):
    files = [os.path.join(dirname, f) for dirname in dirlist
             for f in os.listdir(dirname)
             if os.path.isfile(os.path.join(dirname, f))]

    count_stats = []
    for f in files:
        print(f)
        count_stats.append(read_count(f))

    out = open(txt_output_file, 'w')
    out.write(" ".join(str(k) for k in count_stats))

    plot(count_stats, plot_output_file)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command()
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--output_dir', '-o', help='Output directory',
              required=True)
def run(input_dirs, output_dir):
    input_dirs = [os.path.join(x, '') for x in input_dirs]
    output_dir = os.path.join(output_dir, '')

    if len(input_dirs) > 1:
        base_name = "read_count_summary"
    else:
        input_dirname = os.path.dirname(input_dirs[0])
        path, base_name = os.path.split(input_dirname)

    txt_output_file = os.path.join(output_dir, base_name + ".txt")
    plot_output_file = os.path.join(output_dir, base_name + ".png")

    iof.create_dir(output_dir)
    run_for_dirlist(input_dirs, txt_output_file, plot_output_file)


if __name__ == "__main__":
    run()
