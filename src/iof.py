from Bio import SeqIO

def read_fasta(filename):
    data = {}
    fasta_sequences = SeqIO.parse(open(filename),'fasta')
    for fasta in fasta_sequences:
        name, sequence = fasta.id, str(fasta.seq)

        sample_name = name.split('_')[0]
        if sample_name in data:
            data[sample_name].append(sequence)
        else:
            data[sample_name] = list(sequence)

    return data


def write_distance_matrix(filename, dmatrix):
    pass

if __name__ == "__main__":
    filename = 'data/seqs.fna'
    data = read_fasta(filename)
