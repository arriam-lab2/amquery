import numpy as np
import operator as op
import scipy
from scipy import sparse

# Jenson-Shanon divergence
def jsd(x, y) -> float:
    z = x + y
    d1 = x.multiply(2).divide(z).log2().multiply(x)
    d2 = y.multiply(2).divide(z).log2().multiply(y)

    x = np.sqrt(0.5 * (d1 + d2).sum())
    return x

distances = {'jsd': jsd}


def monkey_patching():
    class positional_map:
        def __init__(self, x, y, fn, default_value=0):
            self.x = x
            self.y = y
            self.fn = fn
            self.default_value = default_value
            self.left = 0
            self.right = 0

        def __iter__(self):
            return self

        def __next__(self):
            lvalue = self._last_value(self.x, self.left)
            rvalue = self._last_value(self.y, self.right)

            x = y = self.default_value
            index = -1
            if lvalue[0] < 0 and rvalue[0] < 0:
                raise StopIteration
            elif lvalue[0] == rvalue[0]:
                self.left += 1
                self.right += 1
                x, y = lvalue[1], rvalue[1]
                index = lvalue[0]
            elif (lvalue[0] < rvalue[0] and lvalue[0] >= 0) or rvalue[0] < 0:
                self.left += 1
                x, y = lvalue[1], self.default_value
                index = lvalue[0]
            else:
                self.right += 1
                x, y = self.default_value, rvalue[1]
                index = rvalue[0]

            return (index, self.fn(x, y))

        def _last_value(self, array, counter):
            if counter < len(array):
                return array[counter]
            else:
                return (-1, self.default_value)

    def divide(self, other):
        x = list(zip(self.indices, self.data))
        y = list(zip(other.indices, other.data))

        z = positional_map(x, y, op.truediv)
        z_indices, z_values = zip(*list((i, v) for i, v in list(z) if v > 0))

        rows = np.array([0 for _ in range(len(z_indices))], dtype=self.dtype)
        return sparse.csr_matrix((z_values, (rows, z_indices)),
                                 self.shape,
                                 dtype=self.dtype)

    _get_index_dtype = scipy.sparse.sputils.get_index_dtype

    def _my_get_index_dtype(*a, **kw):
        kw.pop('check_contents', None)
        return _get_index_dtype(*a, **kw)
    scipy.sparse.compressed.get_index_dtype = _my_get_index_dtype
    scipy.sparse.csr.get_index_dtype = _my_get_index_dtype
    scipy.sparse.bsr.get_index_dtype = _my_get_index_dtype

    def _create_method(op):
        def method(self):
            result = op(self.data)
            x = self._with_data(result, copy=True)
            return x

        method.__name__ = op.__name__
        return method

    setattr(scipy.sparse.csr_matrix, np.log2.__name__, _create_method(np.log2))
    setattr(scipy.sparse.csr_matrix, divide.__name__, divide)


if __name__ == "__main__":
    raise RuntimeError()
else:
    monkey_patching()
