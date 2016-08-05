#!/usr/bin/env python3

import click
from Bio import SeqIO
import os
import os.path
import matplotlib.pyplot as plt
from src.lib import iof


def read_lengths(filename):
    name, extension = os.path.splitext(filename)
    extension = extension[1:]

    length_list = set()
    for seq_record in SeqIO.parse(filename, extension):
        length_list.add(len(seq_record))

    return list(length_list)


def plot(length_list, plot_output_file):
    plt.hist(length_list, normed=1, facecolor='green', alpha=0.5)
    plt.xlabel('Sequence length')
    plt.ylabel('Density')
    plt.title(r'Histogram of sequence length distribution')

    plt.subplots_adjust(left=0.15)
    # plt.show()
    plt.savefig(plot_output_file)


def run_for_dirlist(dirlist, txt_output_file, plot_output_file):
    files = [os.path.join(dirname, f) for dirname in dirlist
             for f in os.listdir(dirname)
             if os.path.isfile(os.path.join(dirname, f))]

    all_lengths = []
    for f in files:
        print(f)
        all_lengths.extend(read_lengths(f))

    out = open(txt_output_file, 'w')
    out.write(" ".join(str(k) for k in all_lengths))

    plot(all_lengths, plot_output_file)


@click.command()
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--output_dir', '-o', help='Output directory')
def run(input_dirs, output_dir):
    input_dirs = [os.path.join(x, '') for x in input_dirs]
    output_dir = os.path.join(output_dir, '')

    if len(input_dirs) > 1:
        base_name = "length_summary"
    else:
        input_dirname = os.path.dirname(input_dirs[0])
        path, base_name = os.path.split(input_dirname)

    txt_output_file = os.path.join(output_dir, base_name + ".txt")
    plot_output_file = os.path.join(output_dir, base_name + ".png")

    iof.make_sure_exists(output_dir)
    run_for_dirlist(input_dirs, txt_output_file, plot_output_file)


if __name__ == "__main__":
    run()
