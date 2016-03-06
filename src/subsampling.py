from itertools import izip
import random
 
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

