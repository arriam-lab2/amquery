#!/usr/bin/env python3

import os
import os.path
from Bio import SeqIO
from Bio import Seq
from typing import Sequence
from .iof import make_sure_exists
import random


def rarefy(config, dirlist: Sequence, max_samples: int):
    files = [os.path.join(dirname, f) for dirname in dirlist
             for f in os.listdir(dirname)
             if os.path.isfile(os.path.join(dirname, f))]

    output_file = os.path.join(config.working_directory,
                               "rarefied.fasta")

    sample_files = []

    num_per_experiment = max_samples // len(dirlist)
    for dirname in dirlist:
        files = [os.path.join(dirname, f)
                 for f in os.listdir(dirname)
                 if os.path.isfile(os.path.join(dirname, f))]

        num = min(num_per_experiment, len(files))
        sample_files.extend(random.sample(files, num))

    merge_fasta_files(sample_files, output_file)


def merge_fasta_files(files: Sequence, output_file: str):
    print("Merging results...")
    with open(output_file, 'w') as outfile:
        for f in files:
            with open(f) as infile:
                for line in infile:
                    outfile.write(line)

    print("Merged to", output_file, ".")


def merge_fasta_from_dirs(dirlist: Sequence, output_file: str):
    files = [os.path.join(dirname, f) for dirname in dirlist
             for f in os.listdir(dirname)
             if os.path.isfile(os.path.join(dirname, f))]

    merge_fasta_files(files)


def split_fasta(dirlist, output_file):
    raise NotImplementedError("Not implemented yet")


def filter_reads(config, input_dirs, min, max, cut, threshold):
    input_dirs = [os.path.join(dirname, '') for dirname in input_dirs]
    output_dir = os.path.join(config.working_directory, '')
    result_dirs = []

    for dirname in input_dirs:
        input_shortname = (os.path.split(os.path.split(dirname)[0]))[1]
        lib_output_dir = os.path.join(output_dir,
                                      input_shortname + ".filtered")
        make_sure_exists(lib_output_dir)
        _filter_sample(config, dirname, lib_output_dir,
                       min, max, cut, threshold)
        result_dirs.append(lib_output_dir)

    return result_dirs


def _filter_sample(config, input_dir: str, output_dir: str,
                   min: int, max: int, cut: int, threshold: int):
    files = [f for f in os.listdir(input_dir)
             if os.path.isfile(os.path.join(input_dir, f))]

    print("Filtering ", input_dir)
    for f in files:
        input_file = os.path.join(input_dir, f)
        output_file = os.path.join(output_dir, f)
        if (not os.path.isfile(output_file)) or config.force:
            _filter_file(input_file, output_file, min, max, cut, threshold)


def _filter_file(input_file: str, output_file: str,
                 min: int, max: int, cut: int, threshold: int):

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
            if cut > 0:
                seq_record.letter_annotations = {}
                seq_record.seq = Seq.Seq(str(seq_record.seq)[:cut])
            sequences.append(seq_record)

    if len(sequences) >= threshold:
        output_handle = open(output_file, "w")
        SeqIO.write(sequences, output_handle, "fasta")
