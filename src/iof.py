from Bio import SeqIO
from collections import defaultdict

def load_seqs(filename):
    data = defaultdict(lambda : defaultdict(str))
    fasta_sequences = SeqIO.parse(open(filename),'fasta')
    for fasta in fasta_sequences:
        name, sequence = fasta.id, str(fasta.seq)
        data[name.split('_')[0]][name] = sequence

    return data

def clear_dir(path):
    import os
    import glob

    files = glob.glob(path + '/*')
    for f in files:
        os.remove(f)

def write_distance_matrix(dmatrix, filename):
    with open(filename, 'w') as f:
        f.write('\t')
        f.write('\n'.join('\t'.join(str(x) for x in line) for line in dmatrix))

    #f.close()

if __name__ == "__main__":
    filename = 'data/seqs.fna'
    data = load_seqs(filename)
    print(data['wood1']['wood1_8560'])

    #a = [['a', 'b', 'c'], ['a', 1, 2, 3], ['b', 4, 5, 6], ['c', 7, 8, 9]] 
    #write_distance_matrix(a, 'tmp.txt')

    pass
