import os
import abc
import biom
import numpy as np
import amquery.utils.iof as iof
from skbio import read
from skbio.tree import TreeNode
from skbio.diversity import beta
from ctypes import cdll, POINTER, c_uint64, c_size_t, c_double


jsdlib = None


class SamplePairwiseDistanceFunction:
    @abc.abstractmethod
    def __call__(self, a, b):
        """
        :param a: Sample 
        :param b: Sample
        :return: float
        """
        raise NotImplementedError

# Jenson-Shanon divergence
class Ffp_JSD(SamplePairwiseDistanceFunction):
    def __init__(self, _):
        pass

    def __call__(self, a, b):
        x = a.kmer_index
        y = b.kmer_index
        xcols_p = x.cols.ctypes.data_as(POINTER(c_uint64))
        xdata_p = x.data.ctypes.data_as(POINTER(c_double))
        ycols_p = y.cols.ctypes.data_as(POINTER(c_uint64))
        ydata_p = y.data.ctypes.data_as(POINTER(c_double))
        return jsdlib.jsd(xcols_p, xdata_p, len(x), ycols_p, ydata_p, len(y))


class WeightedUnifrac(SamplePairwiseDistanceFunction):
    def __init__(self, config):
        biom_fp = config.get("distance", "biom_table")
        tree_path = config.get("distance", "rep_tree")
        failed_fp = config.get("distance", "unaligned")

        assert(biom_fp and tree_path and failed_fp)

        self.otu_table = biom.load_table(biom_fp)
        self.sample_names = self.otu_table.ids(axis="sample")
        self.ids = self.otu_table.ids(axis="observation")

        failed_otus = set(open(failed_fp).read().splitlines())
        self.id_mask = np.array([id_ not in failed_otus for id_ in self.ids], dtype=bool)
        self.masked_ids = self.ids[self.id_mask]

        self.tree = read(tree_path, format="newick", into=TreeNode).root_at_midpoint()

    def __call__(self, a, b):
        """
        :param a: Sample 
        :param b: Sample
        :return: float
        """
        s1 = self.otu_table.data(a.name)[self.id_mask]
        s2 = self.otu_table.data(b.name)[self.id_mask]
        return beta.weighted_unifrac(s1, s2, self.masked_ids, self.tree)


FFP_JSD = 'ffp-jsd'
WEIGHTED_UNIFRAC = 'weighted-unifrac'
DEFAULT_DISTANCE = FFP_JSD
distances = {FFP_JSD: Ffp_JSD, WEIGHTED_UNIFRAC: WeightedUnifrac}


if __name__ == "__main__":
    raise RuntimeError()
else:
    libdir = os.path.dirname(os.path.abspath(__file__))
    jsdlib = cdll.LoadLibrary(iof.find_lib(libdir, "jsd"))
    jsdlib.jsd.argtypes = [POINTER(c_uint64), POINTER(c_double), c_size_t,
                           POINTER(c_uint64), POINTER(c_double), c_size_t]
    jsdlib.jsd.restype = c_double
