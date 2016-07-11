from collections import defaultdict
import glob
import os
import numpy as np
from Bio import SeqIO
from typing import Mapping, List


def normalize(path: str):
    return os.path.join(path, '')


def all_files(dirlist: List[str]) -> List[str]:
    return [os.path.join(dirname, f) for dirname in dirlist
            for f in os.listdir(dirname)
            if os.path.isfile(os.path.join(dirname, f))]


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


def write_distance_matrix(labels, dmatrix, fname):
    with open(fname, "w") as f:
        print("", *map(str, labels), sep="\t", file=f)
        for label, row in zip(labels, dmatrix):
            print(label, *map(str, row), sep="\t", file=f)


def read_distance_matrix(filename: str):
    dmatrix = []
    with open(filename) as f:
        keys = f.readline()[:-1].split("\t")[1:]

        for line in f.readlines():
            values = line[:-1].split("\t")[1:]
            dmatrix.append(values)

        dmatrix = [list(map(float, l)) for l in dmatrix]

    return keys, np.matrix(dmatrix)


def read_coords(filename: str) -> List[str]:
    return [line.rstrip('\n') for line in open(filename)]


if __name__ == "__main__":
    # TODO tests
    #filename = 'data/seqs.fna'
    #data = load_seqs(filename)
    #print(data['wood1']['wood1_8560'])

    filename = "../../out/w_unifrac/wu_full.txt"
    keys, dmatrix = read_distance_matrix(filename)
    print(keys)
    print(dmatrix)