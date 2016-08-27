from collections import defaultdict
import glob
import os
from Bio import SeqIO
from typing import Mapping, List


def normalize(path: str):
    return os.path.join(path, '')


def all_files(dirlist: List[str]) -> List[str]:
    return [os.path.join(dirname, f) for dirname in dirlist
            for f in os.listdir(dirname)
            if os.path.isfile(os.path.join(dirname, f))]


def exists(path: str):
    return os.path.exists(path)


def is_empty(filename: str):
    return os.path.getsize(filename) == 0


def make_sure_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

    return normalize(path)


def load_seqs(filename: str, named: bool=False) -> Mapping:
    data = defaultdict(lambda: defaultdict(str)) if named else defaultdict(list)

    fasta_sequences = SeqIO.parse(open(filename), "fasta")
    for seq_record in fasta_sequences:
        read_id, sequence = seq_record.id, str(seq_record.seq)

        sample_name = read_id.split("_")[0]
        if named:
            data[sample_name][read_id] = sequence
        else:
            data[sample_name].append(sequence)

    return data


def clear(path):
    files = glob.glob(path + "/*")
    for f in files:
        os.remove(f)


def read_coords(filename: str) -> List[str]:
    return [line.rstrip('\n') for line in open(filename)]
