#!/usr/bin/env python3

import numpy as np
import itertools
import json
import random
from amquery.core.storage.vptree.search import neighbors
from amquery.utils.benchmarking import measure_time
from amquery.utils.config import get_storage_path
from amquery.core.storage import Storage


# Vantage-point tree
class BaseVpTree:
    def __init__(self, vp, size, median, left, right):
        self.vp = vp
        self.size = size
        self.median = median
        self.left = left
        self.right = right
    
    def build(self, func, points):
        """
        :param func: Callable
        :param points: np.array
        :return: BaseVpTree
        """
        if len(points) == 1:
            self.vp = points[0]
            self.size = 1
        elif len(points) > 0:
            # Random vantage-point
            vpi = random.randrange(len(points))
            self.vp = points[vpi]
            self.size = 1
            points = np.delete(points, vpi, 0)

            dists = map(func, points, itertools.repeat(self.vp))
            distarr = np.array(list(dists))
            self.median = np.median(distarr)

            # Subtree construction
            leftside = [points[i] for i in range(len(points))
                        if distarr[i] <= self.median]
            rightside = [points[i] for i in range(len(points))
                         if distarr[i] > self.median]

            if len(leftside) > 0:
                self.left = BaseVpTree.from_points(func, leftside)
                self.size += self.left.size
            if len(rightside) > 0:
                self.right = BaseVpTree.from_points(func, rightside)
                self.size += self.right.size

        return self

    def insert(self, point, func):
        if self.size == 0:
            self.vp = point
        else:
            distance_value = func(point, self.vp)
            if not self.median:
                self.median = distance_value

            if distance_value <= self.median:
                if not self.left:
                    self.left = BaseVpTree.from_points(func, [point])
                else:
                    self.left.insert(point, func)
            else:
                if not self.right:
                    self.right = BaseVpTree.from_points(func, [point])
                else:
                    self.right.insert(point, func)

        self.size += 1

    def to_dict(self):
        json_dict = {'vp': self.vp, 'size': self.size }
        if self.median:
            json_dict['median'] = self.median
        if self.left: 
            json_dict['left'] = self.left.to_dict()
        if self.right:
            json_dict['right'] = self.right.to_dict()

        return json_dict

    @classmethod
    def from_dict(cls, json_dict):
        vp = json_dict['vp']
        size = json_dict['size']
        median = json_dict['median'] if 'median' in json_dict else None
        left = cls.from_dict(json_dict['left']) if 'left' in json_dict else None
        right = cls.from_dict(json_dict['right']) if 'right' in json_dict else None
        return cls(vp, size, median, left, right)

    @classmethod
    def from_points(cls, func, points):
        return cls.empty().build(func, points)

    @classmethod
    def from_tree(cls, tree):
        return cls(tree.vp, tree.size, tree.median, tree.left, tree.right)

    @classmethod
    def empty(cls):
        return cls(None, 0, None, None, None)


class VpTree(Storage):
    def __init__(self, vptree = None):
        self.tree = vptree if vptree else BaseVpTree.empty()

    def save(self):
        with open(get_storage_path(), 'w') as outfile:
            json.dump(self.tree.to_dict(), outfile)

    @classmethod
    def load(cls):
        with open(get_storage_path(), 'r') as infile:
            json_dict = json.loads(infile.read())
            return cls(BaseVpTree.from_dict(json_dict))

    #@measure_time(enabled=True)
    def build(self, distance, samples):
        """
        :param distance: PairwiseDistance
        :param samples: Sequence[Sample]
        :return: VpTree
        """
        self.tree.build(distance, np.array([sample.name for sample in samples]))
        return self

    def __len__(self):
        """
        :return: int 
        """
        return self.tree.size if self.tree else 0

    @measure_time(enabled=True)
    def add_samples(self, samples, tree_distance):
        for sample in samples:
            self.tree.insert(sample.name, tree_distance)

    def find(self, distance, sample, k):
        return neighbors(self.tree, distance, sample, k)
