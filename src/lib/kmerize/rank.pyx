import numpy as np
cimport numpy as np

import operator as op

DTYPE = np.uint64
ctypedef np.uint64_t DTYPE_t


def count_kmer_ranks(np.ndarray[np.uint8_t, ndim=1] x, k):
    cdef Py_ssize_t i
    cdef Py_ssize_t n = len(x)
    cdef Py_ssize_t m = 4
    cdef np.uint8_t [:] xview = x

    if n == 0:
        return []

    cdef np.ndarray[DTYPE_t, ndim=1] ranks = np.zeros(n-k+1, dtype=DTYPE)

    for i in range(k):
        ranks[0] += xview[i] * (m ** (k-i-1))

    for i in range(1, n-k+1):
        ranks[i] = m * (ranks[i-1] - xview[i-1] * m**(k - 1)) + xview[i+k-1]

    return ranks
