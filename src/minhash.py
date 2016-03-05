import mmh3
import heapq
import numpy as np

# murmur3 algorithm
def hash(string):
    return mmh3.hash(string)
    #return mmh3.hash64(str)

def kmer_hasher(string, k):
    kmer = string[:k]

    for i in range(len(string) - k):
        kmer = kmer[1:] + string[i + k]
        yield hash(kmer)

def minhash(strings, kmer_size, count):
    array = np.array([x for s in strings for x in kmer_hasher(s, kmer_size)])
    #print(array)
    result = heapq.nsmallest(count, range(len(array)), array.take)
    #print(' '.join(str(array[x]) for x in result))
    return result
        

if __name__ == "__main__":
    mh = minhash(["297815197236451293", "2236613461346", "34653453453"], 5, 3)
    print(mh)
