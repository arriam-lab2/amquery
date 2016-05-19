from collections import defaultdict
import glob
import os

import numpy as np
from Bio import SeqIO


def load_seqs(fname):
    data = defaultdict(lambda: defaultdict(str))
    fasta_sequences = SeqIO.parse(open(fname), "fasta")
    for fasta in fasta_sequences:
        name, sequence = fasta.id, str(fasta.seq)
        data[name.split("_")[0]][name] = sequence

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
