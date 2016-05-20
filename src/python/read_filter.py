import click
from Bio import SeqIO
from Bio import Seq
import os
import os.path
from src.lib import iof


def run_filter(input_dir: str, output_dir: str,
               min: int, max: int, cut: int, threshold: int):
    files = [f for f in os.listdir(input_dir)
             if os.path.isfile(os.path.join(input_dir, f))]

    for f in files:
        input_file = os.path.join(input_dir, f)
        output_file = os.path.join(output_dir, f)
        filter_file(input_file, output_file, min, max, cut, threshold)


def filter_file(input_file: str, output_file: str,
                min: int, max: int, cut: int, threshold: int):
    print(input_file)

    leftside, extension = os.path.splitext(input_file)
    extension = extension[1:]
    sample_id = os.path.split(leftside)[1]

    count = 0
    sequences = []
    for seq_record in SeqIO.parse(input_file, extension):
        # filter by read length
        if len(seq_record.seq) >= min:
            # renaming a seq record
            seq_record.id = sample_id + "_" + str(count)
            count += 1
            seq_record.letter_annotations = {}
            seq_record.seq = Seq.Seq(str(seq_record.seq)[:cut])
            sequences.append(seq_record)

    if len(sequences) >= threshold:
        output_handle = open(output_file, "w")
        SeqIO.write(sequences, output_handle, "fasta")


@click.command()
@click.argument('input_dirs', type=click.Path(exists=True), nargs=-1,
                required=True)
@click.option('--output_dir', '-o', help='Output directory',
              required=True)
@click.option('--min', type=int, help='Minimal read length',
              required=True)
@click.option('--max', type=int, help='Maximal read length')
@click.option('--cut', type=int, required=True,
              help='Right-hand side cut point for read clipping')
@click.option('--threshold', type=int, help='Minimal read count per sample',
              required=True)
def run(input_dirs, output_dir, min, max, cut, threshold):
    input_dirs = [os.path.join(dirname, '') for dirname in input_dirs]
    output_dir = os.path.join(output_dir, '')

    for dirname in input_dirs:
        input_shortname = (os.path.split(os.path.split(dirname)[0]))[1]
        lib_output_dir = os.path.join(output_dir,
                                      input_shortname + ".filtered")
        iof.create_dir(lib_output_dir)
        run_filter(dirname, lib_output_dir, min, max, cut, threshold)


if __name__ == "__main__":
    run()
