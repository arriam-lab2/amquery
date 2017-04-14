#!/usr/bin/env python3

import itertools
import random
import numpy as np
import json
from typing import Callable, Any, Sequence, Mapping, Tuple

from amquery.core.distance import PwMatrix
from amquery.core.sample import Sample
from amquery.core.sample_map import SampleMap
from amquery.core.tree.search import neighbors
from amquery.utils.config import Config
from amquery.utils.benchmarking import measure_time


# Vantage-point tree
class BaseVpTree:
    def __init__(self, vp, size, median, left, right):
        self.vp = vp
        self.size = size
        self.median = median
        self.left = left
        self.right = right
    
    def build(self, points: np.array, func: Callable):
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
                self.left = BaseVpTree.from_points(leftside, func)
                self.size += self.left.size
            if len(rightside) > 0:
                self.right = BaseVpTree.from_points(rightside, func)
                self.size += self.right.size

        return self

    def insert(self, point: Any, func: Callable):
        if self.size == 0:
            self.vp = point
        else:
            distance_value = func(point, self.vp)
            if not self.median:
                self.median = distance_value

            if distance_value <= self.median:
                if not self.left:
                    self.left = BaseVpTree.from_points([point], func)
                else:
                    self.left.insert(point, func)
            else:
                if not self.right:
                    self.right = BaseVpTree.from_points([point], func)
                else:
                    self.right.insert(point, func)

        self.size += 1

    def to_dict(self):
        json_dict = {'vp': self.vp.name, 'size': self.size }
        if self.median:
            json_dict['median'] = self.median
        if self.left: 
            json_dict['left'] = self.left.to_dict()
        if self.right:
            json_dict['right'] = self.right.to_dict()

        return json_dict

    @classmethod
    def from_dict(cls, json_dict: Mapping, sample_map: SampleMap):
        vp = sample_map[json_dict['vp']]
        size = json_dict['size']
        median = json_dict['median'] if 'median' in json_dict else None
        left = cls.from_dict(json_dict['left'], sample_map) if 'left' in json_dict else None
        right = cls.from_dict(json_dict['right'], sample_map) if 'right' in json_dict else None
        return cls(vp, size, median, left, right)

    @classmethod
    def from_points(cls, points: np.array, func: Callable):
        return cls.empty().build(points, func)

    @classmethod
    def from_tree(cls, tree):
        return cls(tree.vp, tree.size, tree.median, tree.left, tree.right)

    @classmethod
    def empty(cls):
        return cls(None, 0, None, None, None)


class TreeDistance:
    def __init__(self, pwmatrix: PwMatrix):
        self.pwmatrix = pwmatrix

    def __call__(self, a: Sample, b: Sample):
        return self.pwmatrix[a, b]

    @property
    def samples(self) -> Sequence[Any]:
        return self.pwmatrix.sample_map.samples

    def add_sample(self, sample: Sample) -> None:
        self.pwmatrix.add_sample(sample)


class VpTree:
    def __init__(self, config: Config, vptree: BaseVpTree = None):
        self.tree = vptree if vptree else BaseVpTree.empty()
        self.config = config

    def save(self):
        with open(self.config.vptree_path, 'w') as outfile:
            json.dump(self.tree.to_dict(), outfile)

    @classmethod
    def load(cls, config: Config, sample_map: SampleMap):
        with open(config.vptree_path, 'r') as infile:
            json_dict = json.loads(infile.read())
            return cls(config, BaseVpTree.from_dict(json_dict, sample_map))

    @measure_time(enabled=True)
    def build(self, tree_distance: Callable):
        self.tree.build(list(tree_distance.samples), tree_distance)
        return self

    @measure_time(enabled=True)
    def add_samples(self,
                    samples: Sequence[Sample],
                    tree_distance: Callable):
        for sample_file in samples:
            self.add_sample(sample_file, tree_distance)

    def add_sample(self,
                   sample: Sample,
                   tree_distance: Callable):
        tree_distance.add_sample(sample)
        self.tree.insert(sample, tree_distance)

    def search(self, query_point: Any, k: int,
               tree_distance: Callable) -> Tuple[np.array, np.array]:
        return neighbors(self.tree, query_point, k, tree_distance)
