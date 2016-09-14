import unittest
import numpy as np
from sklearn.neighbors import NearestNeighbors

from lib.tree.vptree import BaseVpTree, euclidean
import lib.tree.search as vpsearch


class TestVptree(unittest.TestCase):
    def test_search(self):
        n = 100
        x = np.random.uniform(0, 10, n)
        y = np.random.uniform(0, 10, n)
        points = np.array(list(zip(x, y)))

        k = 50
        tree = BaseVpTree(points, euclidean)
        nbrs = NearestNeighbors(n_neighbors=k,
                                algorithm='ball_tree').fit(points)

        for p in points:
            y1, _ = vpsearch.neighbors(tree, p, k)
            y2, _ = nbrs.kneighbors([p])
            y2 = y2[0]
            self.assertTrue(np.array_equal(y1, y2))

    def test_insert(self):
        pass

if __name__ == '__main__':
    unittest.main()
