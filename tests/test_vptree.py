import os
import unittest
import numpy as np
import tempfile
import string
import random
from sklearn.neighbors import NearestNeighbors

from amquery.core.tree.vptree import VpTree


class ConfigMock:
    pass

class SampleMock:
    def __init__(self, name, values):
        self.name = name
        self.values = values

def euclidean(a: np.array, b: np.array):
    return np.linalg.norm(a - b)

class SampleDistanceMock:
    def __init__(self, function, sample_map):
        self.f = function
        self.sample_map = sample_map

    def __call__(self, a: SampleMock, b: SampleMock):
        return self.f(a.values, b.values)

    @property
    def samples(self):
        return self.sample_map.values()

    def add_sample(self, sample):
        self.sample_map[sample.name] = sample

class SampleMapMock(dict):
    pass

def random_name():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class TestVptree(unittest.TestCase):
    def setUp(self):
        # index size
        self.n = 20
        # dimensionality
        self.m = 3
        # number of neighbors
        self.k = 5

        self.samples = [SampleMock(random_name(), np.random.uniform(0, 1, self.m)) for _ in range(self.n)]
        self.points = np.array(list(x.values for x in self.samples))
        self.sample_map = SampleMapMock({x.name: x for x in self.samples})
        self.config = ConfigMock()
        self.distance = SampleDistanceMock(euclidean, self.sample_map)
        self.tree = VpTree(self.config)
        self.tree.build(self.distance)

        vptree_file = tempfile.NamedTemporaryFile(delete=False)
        self.config.vptree_path = vptree_file.name


    def test_search(self):
        self._test_search(self.tree)

    def _test_search(self, vptree_obj):
        nbrs = NearestNeighbors(n_neighbors=self.k,
                                algorithm='ball_tree').fit(self.points)

        for name, sample in self.sample_map.items():
            y1, _ = vptree_obj.search(sample, self.k, self.distance)
            y2, _ = nbrs.kneighbors(sample.values)
            y2 = y2[0]
            self.assertTrue(np.array_equal(y1, y2))

    def test_save_load(self):
        self.tree.save()
        tree = VpTree.load(self.config, self.sample_map)

        self._test_search(tree)
        self.assertTrue(self.tree.tree.to_dict() == tree.tree.to_dict())

    def test_insert(self):
        # backup the tree
        self.tree.save()
        tree = VpTree.load(self.config, self.sample_map)

        # add new samples to the tree
        new_samples = [SampleMock(random_name(), np.random.uniform(0, 1, self.m)) for _ in range(self.n)]
        self.samples += new_samples
        self.sample_map.update(SampleMapMock({x.name: x for x in new_samples}))
        self.tree.add_samples(new_samples, self.distance)

        self.points = np.array(list(x.values for x in self.samples))
        self._test_search(self.tree)

        # add to the exported tree
        tree.add_samples(new_samples, self.distance)
        self._test_search(tree)

    def tearDown(self):
        os.unlink(self.config.vptree_path)

if __name__ == '__main__':
    unittest.main()
