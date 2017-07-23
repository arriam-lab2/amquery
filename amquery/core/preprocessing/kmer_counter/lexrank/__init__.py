if __name__ == "__main__":
    raise RuntimeError()
else:
    import os
    from ctypes import cdll, POINTER, c_uint8, c_uint64, c_size_t, c_int
    import amquery.utils.iof as iof

    libdir = os.path.dirname(os.path.abspath(__file__))
    ranklib = cdll.LoadLibrary(iof.find_lib(libdir, "lexrank"))
    ranklib.count_kmer_ranks.argtypes = [POINTER(c_uint8), POINTER(c_uint64),
                                         c_size_t, c_int]



__license__ = "MIT"
__version__ = "0.2.1"
__author__ = "Nikolay Romashchenko"
__maintainer__ = "Nikolay Romashchenko"
__email__ = "nikolay.romashchenko@gmail.com"
__status__ = "Development"
