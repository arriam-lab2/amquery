import itertools
import time
from Bio import SeqIO
from collections import Counter
from itertools import izip

import scipy
from scipy import stats

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
    [tables.update({sample: hasher(data[sample], k)}) for sample in data.keys()]

    for pair in itertools.combinations(tables, r=2):
        table1 = tables[pair[0]].copy()
        table2 = tables[pair[1]].copy()

        print(pair[0] + " vs. " + pair[1] + ": ")
        #jackknifed_distance(table1, table2)
        distance(table1, table2)


def distance(table1, table2):
    value = jaccard(set(table1.values()), set(table2.values()))
    print(value)


# отобрать подмножество без возвращений
def jackknifed_distance(table1, table2):
    subset_size = 1000
    values = [jaccard(set(x), set(y)) for x, y in zipped_jackknife(table1, table2, subset_size)]
    print(str(scipy.stats.bayes_mvs(values)))

    #print(pair[0] + " vs. " + pair[1] + ": " + str(values))


# Jaccard index of similarity
def jaccard(x, y):
    intersection = len(set.intersection(x, y))
    union = len(set.union(x, y))
    return 1 - (intersection / float(union))

# Bray-Curtis dissimilarity
#def bray_curtis(x, y):
    #intersection = len(set.intersection(x, y))
#    pass

    # Jenson-Shanon divergence
def JSD(x, y):
    from scipy.stats import entropy
    from numpy.linalg import norm
    import numpy as np

    print(x)
    x = x / norm(x, ord=1)
    print(x)
    y = y / norm(y, ord=1)
    z = 0.5 * (x + y)
    jsd = 0.5 * entropy(x, z) + 0.5 * entropy(y, z)
    return jsd
    #return sqrt(jsd)

 
def zipped_jackknife(x, y, subset_size):
    for xi, yi in izip(jackknifed(x, subset_size), 
                       jackknifed(y, subset_size)):
        yield (xi, yi)


# jackknife resampling generator
def jackknifed(table, chunk_size):
    yield table
    while len(table) > 0:
        #print("J", len(table))
        [table.pop(x) for x in [key for key in table.keys()][:chunk_size]]
        yield table


if __name__ == "__main__":
    
    start = time.time()

    k = 50
    filename = 'data/seqs.fna'
    data = read_data(filename)
    distance_matrix(data, k)

    #table1 = {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7}
    #table2 = {1:1, 13:9, 5:5, 16:3, 7:10}
    #print('\n'.join(str(x) for x in jackknifed(table1, 2)))
    #print(JSD(Counter(table1), Counter(table2)))

    end = time.time()
    print("Time: ", end - start)


