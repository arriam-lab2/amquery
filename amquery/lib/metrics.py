import os
from ctypes import cdll, POINTER, c_uint64, c_size_t, c_double

from amquery.lib.sparse import SparseArray
import amquery.lib.iof as iof

jsdlib = None


# Jenson-Shanon divergence
def jsd(x: SparseArray, y: SparseArray) -> float:
    xcols_p = x.cols.ctypes.data_as(POINTER(c_uint64))
    xdata_p = x.data.ctypes.data_as(POINTER(c_double))

    ycols_p = y.cols.ctypes.data_as(POINTER(c_uint64))
    ydata_p = y.data.ctypes.data_as(POINTER(c_double))

    return jsdlib.jsd(xcols_p, xdata_p, len(x),
                      ycols_p, ydata_p, len(y))

distances = {'jsd': jsd}


if __name__ == "__main__":
    raise RuntimeError()
else:
    libdir = os.path.dirname(os.path.abspath(__file__))
    jsdlib = cdll.LoadLibrary(iof.find_lib(libdir, "jsd"))
    jsdlib.jsd.argtypes = [POINTER(c_uint64), POINTER(c_double), c_size_t,
                           POINTER(c_uint64), POINTER(c_double), c_size_t]
    jsdlib.jsd.restype = c_double
