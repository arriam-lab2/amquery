import numpy as np
cimport numpy as np

DTYPE = np.uint64
ctypedef np.uint64_t DTYPE_t


def lexicographic_rank(x, alphabet):
    cdef Py_ssize_t i, j
    cdef DTYPE_t n = len(alphabet)
    cdef DTYPE_t result = 0

    for i in range(len(x)):
        result += alphabet[x[i]] * (n ** (len(x) - i - 1))

    return result
