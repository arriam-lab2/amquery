import itertools
import random
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


def distance_matrix(data, k, jk_size):
    # all pairs [sample, hash table]
    tables = {}
    [tables.update({sample: hasher(data[sample], k)}) for sample in data.keys()]

    for pair in itertools.combinations(tables, r=2):
        table1 = tables[pair[0]].copy()
        table2 = tables[pair[1]].copy()
        #print(len(table1))
        #print(len(table2))

        print(pair[0] + " vs. " + pair[1] + ": ")
        jackknifed_distance(table1, table2, jk_size)
        #distance(table1, table2)


def distance(table1, table2):
    value = jaccard(set(table1.values()), set(table2.values()))
    #value = JSD(set(table1.values()), set(table2.values()))
    print(value)


def jackknifed_distance(table1, table2, subset_size):
    values = [jaccard(set(x), set(y)) for x, y in zipped_jackknife(table1, table2, subset_size)]
    print(str(scipy.stats.bayes_mvs(values)))


# Jaccard index of similarity
def jaccard(x, y):
    intersection = len(set.intersection(x, y))
    union = len(set.union(x, y))
    return 1 - (intersection / float(union))

# Bray-Curtis dissimilarity
#def bray_curtis(x, y):
#intersection = len(set.intersection(x, y))
#pass

# Jenson-Shanon divergence
def JSD(x, y):
    import numpy as np
    import warnings
    warnings.filterwarnings("ignore", category = RuntimeWarning)
    x = np.array(x)
    y = np.array(y)
    d1 = x*np.log2(2*x/(x+y))
    d2 = y*np.log2(2*y/(x+y))
    d1[np.isnan(d1)] = 0
    d2[np.isnan(d2)] = 0
    return sqrt(0.5 * np.sum(d1 + d2))

 
def zipped_jackknife(x, y, subset_size):
    for xi, yi in izip(jackknifed(x, subset_size), 
                       jackknifed(y, subset_size)):
        yield (xi, yi)


# jackknife resampling generator
def jackknifed(table, chunk_size):
    yield table
    while len(table) > 0:
        keys = random.sample(table.keys(), min(chunk_size, len(table)))
        chunk = {}
        x = [chunk.update({key: table.pop(key)}) for key in keys]
        yield chunk


if __name__ == "__main__":
    
    from time import time
    start = time()

    random.seed(42)
    k = 50
    jackknife_subset_size = 1000
    filename = 'data/seqs.fna'
    data = read_data(filename)
    distance_matrix(data, k, jackknife_subset_size)

    #table1 = {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7}
    #print('\n'.join(str(t) for t in jackknifed(table1, 2)))
    #table2 = {1:1, 13:9, 5:5, 16:3, 7:10}
    #print('\n'.join(str(x) for x in jackknifed(table1, 2)))
    #print(JSD(Counter(table1), Counter(table2)))

    end = time()
    print("Time: " + str(end - start))


