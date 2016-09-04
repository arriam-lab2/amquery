import numpy as np
cimport numpy as np

DTYPE = np.uint64
ctypedef np.uint64_t DTYPE_t


def lexicographic_rank(string, alphabet):
    cdef Py_ssize_t i
    cdef DTYPE_t n = len(alphabet)
    cdef DTYPE_t result = 0

    for i in range(len(string)):
        result += alphabet[string[i]] * (n ** (len(string) - i - 1))

    return result


def count_kmer_ranks(string, k, alphabet):
    cdef Py_ssize_t i
    cdef Py_ssize_t n = len(string)
    cdef Py_ssize_t m = len(alphabet)

    cdef np.ndarray[DTYPE_t, ndim=1] ranks = np.zeros(n - k + 1, dtype=DTYPE)

    for i in range(k):
        ranks[0] += alphabet[string[i]] * (m ** (k - i - 1))

    for i in range(1, n - k + 1):
        ranks[i] = m * (ranks[i - 1] - alphabet[string[i - 1]] *
            m ** (k - 1)) + alphabet[string[i + k - 1]]

    return ranks
