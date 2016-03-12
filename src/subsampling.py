#from itertools import zip
import random
import biom
import re
import iof
from collections import defaultdict
 
def zipped_jackknife(x, y, subset_size):
    for xi, yi in zip(jackknifed(x, subset_size), 
                       jackknifed(y, subset_size)):
        yield (xi, yi)


MAX_COUNT = 10

# jackknife resampling generator
def jackknifed(table, chunk_size):
    #yield table

    count = 0
    while count < MAX_COUNT:
        for key in table.keys():
            sample_size = min(chunk_size, len(table[key]))
            to_exclude = random.sample(table[key], sample_size)
            [table[key].remove(x) for x in to_exclude]
        
        count = count + 1
        yield table


def get_class(read_id):
    return read_id.split('_')[0]


def load_seqs_otus_map(filename):
    so_map = {}
    lines = [line.rstrip('\n') for line in open(filename)]
    for line in lines:
        items = line.split('\t')
        so_map[items[0]] = items[1:]

    for otu in so_map:
        d = defaultdict(list)
        for value in so_map[otu]:
            d[get_class(value)].append(value)

        so_map[otu] = d

    return so_map


def subsample(biom_table, seqs, so_map, out_file):
    ids = biom_table.ids(axis="observation")
    reads = []
    for obs in ids:
        read_map = zip(biom_table.ids(), biom_table.data(obs, axis="observation").astype(int))

        for cls, count in read_map:
            reads.extend(random.sample(so_map[obs][cls], count))

    with open(out_file, 'w') as f:
        s = '\n'.join('>' + x + '\n' + seqs[get_class(x)][x] for x in reads)
        f.write(s)


if __name__ == "__main__":
    #table = {'a':[1, 2, 3, 4], 'b':[2, 4, 6, 8, 10], 'c':[3, 6, 9, 12, 15, 18]}
    #print('\n'.join(str(t) for t in jackknifed(table, 2)))

    so_map_file = '../data/mikkele/seqs_otus.txt'
    so_map = load_seqs_otus_map(so_map_file)
    #print(so_map)

    seqs = iof.load_seqs('../data/mikkele/seqs.fna')

    otu_dir = '../data/mikkele/out_rarefied_otu'
    filename = '1.biom'
    table = biom.load_table(otu_dir + '/' + filename)

    out_dir = './data/out_rarefied'
    subsample(table, seqs, so_map, out_dir + '/' + '1.fna')


