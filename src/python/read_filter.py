import click
from Bio import SeqIO
import os
import os.path
import iof


def run_filter(input_dir, output_dir, min, max):
    files = [f for f in os.listdir(input_dir)
             if os.path.isfile(os.path.join(input_dir, f))]

    for f in files:
        input_file = os.path.join(input_dir, f)
        output_file = os.path.join(output_dir, f)
        filter_file(input_file, output_file, min, max)


def filter_file(input_file, output_file, min, max):
    print(input_file)

    leftside, extension = os.path.splitext(input_file)
    extension = extension[1:]
    sample_id = os.path.split(leftside)[1]

    count = 0
    sequences = []
    for seq_record in SeqIO.parse(input_file, extension):
        # filter by read length
        if (len(seq_record) >= min and len(seq_record) <= max):
            # renaming a seq record
            seq_record.id = sample_id + "_" + str(count)
            count += 1
            sequences.append(seq_record)

    output_handle = open(output_file, "w")
    SeqIO.write(sequences, output_handle, "fasta")


@click.command()
@click.option('--input_dir', '-i', help='Input directory',
              required=True)
@click.option('--output_dir', '-o', help='Output directory',
              required=True)
@click.option('--min', type=int, help='Minimal read length',
              required=True)
@click.option('--max', type=int, help='Maximal read length')
def run(input_dir, output_dir, min, max):
    input_dir = os.path.join(input_dir, '')
    output_dir = os.path.join(output_dir, '')
    input_shortname = (os.path.split(os.path.split(input_dir)[0]))[1]
    output_dir += input_shortname + ".filtered"

    iof.create_dir(output_dir)
    run_filter(input_dir, output_dir, min, max)


if __name__ == "__main__":
    run()
