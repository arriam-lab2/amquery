from Bio import SeqIO
from collections import defaultdict
import os


def load_seqs(filename):
    data = defaultdict(lambda: defaultdict(str))
    fasta_sequences = SeqIO.parse(open(filename), 'fasta')
    for fasta in fasta_sequences:
        name, sequence = fasta.id, str(fasta.seq)
        data[name.split('_')[0]][name] = sequence

    return data


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def clear_dir(path):
    import glob

    files = glob.glob(path + '/*')
    for f in files:
        os.remove(f)


def write_distance_matrix(dmatrix, filename):
    with open(filename, 'w') as f:
        f.write('\t')
        f.write('\n'.join('\t'.join(str(x) for x in line) for line in dmatrix))


def read_distance_matrix(filename):
    dmatrix = []
    with open(filename, 'r') as f:
        keys = f.readline()[:-1].split('\t')[1:]

        for line in f.readlines():
            values = line[:-1].split('\t')[1:]
            dmatrix.append(values)

        dmatrix = [list(map(float, l)) for l in dmatrix]

    return keys, dmatrix


if __name__ == "__main__":
    #filename = 'data/seqs.fna'
    #data = load_seqs(filename)
    #print(data['wood1']['wood1_8560'])

    filename = '../../out/w_unifrac/wu_full.txt'
    keys, dmatrix = read_distance_matrix(filename)
    print(keys)
    print(dmatrix)
