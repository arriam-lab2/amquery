#!/usr/bin/env python3

import click
from Bio import SeqIO
import os
import os.path
import matplotlib.pyplot as plt
import iof


def read_lengths(filename):
    name, extension = os.path.splitext(filename)
    extension = extension[1:]

    length_list = []
    for seq_record in SeqIO.parse(filename, extension):
        length_list.append(len(seq_record))

    return length_list


def plot(length_list, plot_output_file):
    plt.hist(length_list, normed=1, facecolor='green', alpha=0.5)
    plt.xlabel('Sequence length')
    plt.ylabel('Density')
    plt.title(r'Histogram of sequence length distribution')

    plt.subplots_adjust(left=0.15)
    # plt.show()
    plt.savefig(plot_output_file)


def run_for_dir(dirname, txt_output_file, plot_output_file):
    files = [os.path.join(dirname, f) for f in os.listdir(dirname)
             if os.path.isfile(os.path.join(dirname, f))]

    all_lengths = []
    for f in files:
        all_lengths.extend(read_lengths(f))

    out = open(txt_output_file, 'w')
    out.write(" ".join(str(k) for k in all_lengths))

    plot(all_lengths, plot_output_file)


# def run_for_dirs(dirlist, txt_output_file, plot_output_file):
# pass


@click.command()
@click.option('--input_dir', '-i', help='Input directory')
@click.option('--output_dir', '-o', help='Output directory')
def run(input_dir, output_dir):
    input_dir = os.path.join(input_dir, '')
    output_dir = os.path.join(output_dir, '')

    iof.create_dir(output_dir)

    input_dirname = os.path.dirname(input_dir)
    path, base_name = os.path.split(input_dirname)
    txt_output_file = os.path.join(output_dir, base_name + ".txt")
    plot_output_file = os.path.join(output_dir, base_name + ".png")

    run_for_dir(input_dir, txt_output_file, plot_output_file)


if __name__ == "__main__":
    run()
