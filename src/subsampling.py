#from itertools import zip
import random
 
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


if __name__ == "__main__":
    table = {'a':[1, 2, 3, 4], 'b':[2, 4, 6, 8, 10], 'c':[3, 6, 9, 12, 15, 18]}
    print('\n'.join(str(t) for t in jackknifed(table, 2)))


