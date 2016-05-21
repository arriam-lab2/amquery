#!/usr/bin/env python3

import os
import os.path
from Bio import SeqIO
from Bio import Seq
from typing import Sequence
from .iof import make_sure_exists


def prebuild(config, dirlist: Sequence,
             single_file: bool):
    if single_file:
        pass
        #split_fasta(config, dirlist, output_dir)
    else:
        pass
        #merge_fasta()


def merge_fasta(dirlist: Sequence, output_file: str):
    files = [os.path.join(dirname, f) for dirname in dirlist
             for f in os.listdir(dirname)
             if os.path.isfile(os.path.join(dirname, f))]

    with open(output_file, 'w') as outfile:
        for f in files:
            with open(f) as infile:
                print(f)
                for line in infile:
                    outfile.write(line)


def split_fasta(dirlist, output_file):
    pass


def filter_reads(input_dirs, output_dir, min, max, cut, threshold):
    input_dirs = [os.path.join(dirname, '') for dirname in input_dirs]
    output_dir = os.path.join(output_dir, '')
    for dirname in input_dirs:
        input_shortname = (os.path.split(os.path.split(dirname)[0]))[1]
        lib_output_dir = os.path.join(output_dir,
                                      input_shortname + ".filtered")
        make_sure_exists(lib_output_dir)
        _filter_sample(dirname, lib_output_dir, min, max, cut, threshold)


def _filter_sample(input_dir: str, output_dir: str,
                   min: int, max: int, cut: int, threshold: int):
    files = [f for f in os.listdir(input_dir)
             if os.path.isfile(os.path.join(input_dir, f))]

    for f in files:
        input_file = os.path.join(input_dir, f)
        output_file = os.path.join(output_dir, f)
        _filter_file(input_file, output_file, min, max, cut, threshold)


def _filter_file(input_file: str, output_file: str,
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
            if cut > 0:
                seq_record.letter_annotations = {}
                seq_record.seq = Seq.Seq(str(seq_record.seq)[:cut])
            sequences.append(seq_record)

    if len(sequences) >= threshold:
        output_handle = open(output_file, "w")
        SeqIO.write(sequences, output_handle, "fasta")
