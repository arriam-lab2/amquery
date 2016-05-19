from collections import defaultdict
import glob
import os
import numpy as np
from Bio import SeqIO
from typing import Mapping


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


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def clear_dir(path):
    files = glob.glob(path + "/*")
    for f in files:
        os.remove(f)


def write_distance_matrix(labels, dmatrix, fname):
    with open(fname, "w") as f:
        print("", *map(str, labels), sep="\t", file=f)
        for label, row in zip(labels, dmatrix):
            print(label, *map(str, row), sep="\t", file=f)


def read_distance_matrix(filename):
    dmatrix = []
    with open(filename) as f:
        keys = f.readline()[:-1].split("\t")[1:]

        for line in f.readlines():
            values = line[:-1].split("\t")[1:]
            dmatrix.append(values)

        dmatrix = [list(map(float, l)) for l in dmatrix]

    return keys, np.matrix(dmatrix)


if __name__ == "__main__":
    # TODO tests
    #filename = 'data/seqs.fna'
    #data = load_seqs(filename)
    #print(data['wood1']['wood1_8560'])

    filename = "../../out/w_unifrac/wu_full.txt"
    keys, dmatrix = read_distance_matrix(filename)
    print(keys)
    print(dmatrix)
