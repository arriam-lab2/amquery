import itertools
import time
from Bio import SeqIO

def read_data(filename):
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


# Jaccard index of similarity
def jaccard(x, y):
    intersection = len(set.intersection(x, y))
    union = len(set.union(x, y))
    return intersection / float(union)

# Bray-Curtis dissimilarity
def bray_curtis(x, y):
    intersection = len(set.intersection(x, y))
    pass

 
def kmer_generator(string, k):
    kmer = string[:k]

    for i in range(len(string) - k):
        kmer = kmer[1:] + string[i + k]
        yield kmer

def hasher(string_set, k):
    table = {}
    for string in string_set:
        for kmer in kmer_generator(string, k):
            if kmer in table:
                table[kmer] = table[kmer] + 1
            else:
                table[kmer] = 1

    return table


def distance_matrix(data, k):
    # all pairs [sample, hash table]
    tables = {}
    tables.update([sample, hasher(data[sample], k)] for sample in data.keys())

    for pair in itertools.combinations(tables, r=2):
        #print(pair[0] + " vs. " + pair[1] + ": " + 
                #str(jaccard(set(pair[0]), set(pair[1]))))
        print(pair[0] + " vs. " + pair[1])


# jackknife-resampling generator
def jackknifed(table, chunk_size):
    yield table
    while len(table) > 0:
        [table.pop(x) for x in [key for key in table.keys()][:chunk_size]]
        yield table


if __name__ == "__main__":
    
    start = time.time()

    k = 50
    filename = 'data/seqs.fna'
    data = read_data(filename)
    distance_matrix(data, k)

    table = {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7}
    print('\n'.join(str(x) for x in jackknifed(table, 2)))

    end = time.time()
    print("Time: ", end - start)


