#!/usr/bin/env python3

import click
import os
import os.path
import iof
import random


def random_dna(length):
    return ''.join(random.choice('ACGT') for _ in range(length))


def barcode(sample_id):
    return random_dna(10)


def primer(sample_id):
    return random_dna(20)


def treatment(sample_id):
    return "treatment"


def reverse_primer(sample_id):
    return random_dna(20)


def description(sample_id):
    return "description"


def create_map_element(sample_id):
    result = [sample_id]
    result.append(barcode(sample_id))
    result.append(primer(sample_id))
    result.append(treatment(sample_id))
    result.append(reverse_primer(sample_id))
    result.append(description(sample_id))
    return result


def create_map(dirlist, output_file):
    files = [os.path.join(dirname, f) for dirname in dirlist
             for f in os.listdir(dirname)
             if os.path.isfile(os.path.join(dirname, f))]

    header_elements = ['#SampleID', 'BarcodeSequence', 'LinkerPrimerSequenc',
                       'Treatment', 'ReversePrimer', 'Description']

    elements = [header_elements]
    for f in files:
        name, extension = os.path.splitext(f)
        sample_id = os.path.split(name)[1]
        element = create_map_element(sample_id)
        elements.append(element)

    out = open(output_file, 'w')
    out.write("\n".join("\t".join(x for x in e) for e in elements))


@click.command()
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--output_dir', '-o', help='Output directory',
              required=True)
def run(input_dirs, output_dir):
    input_dirs = [os.path.join(x, '') for x in input_dirs]
    output_dir = os.path.join(output_dir, '')
    output_file = os.path.join(output_dir, "map.txt")
    iof.create_dir(output_dir)
    create_map(input_dirs, output_file)


if __name__ == "__main__":
    run()
