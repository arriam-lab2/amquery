#!/usr/bin/env python3

import itertools
import random
import numpy as np
import joblib
from typing import Callable, Any, Sequence

from amquery.index.distance import PwMatrix
from amquery.index.coord_system import CoordSystem
from amquery.index.sample import Sample

from amquery.utils.config import Config
from amquery.utils.benchmarking import measure_time


# Vantage-point tree
class BaseVpTree:

    def __init__(self, points: np.array, func: Callable):
        self.size = 0
        self.left = None
        self.right = None
        self.median = None

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
                self.left = BaseVpTree(leftside, func)
                self.size += self.left.size
            if len(rightside) > 0:
                self.right = BaseVpTree(rightside, func)
                self.size += self.right.size

    def insert(self, point: Any, func: Callable):
        if self.size == 0:
            self.vp = point
        else:
            distance_value = func(point, self.vp)
            if not self.median:
                self.median = distance_value

            if distance_value <= self.median:
                if not self.left:
                    self.left = BaseVpTree([point], func)
                else:
                    self.left.insert(point, func)
            else:
                if not self.right:
                    self.right = BaseVpTree([point], func)
                else:
                    self.right.insert(point, func)

        self.size += 1


def euclidean(a: np.array, b: np.array):
    return np.linalg.norm(a - b)


# Euclidean distance in a proper coordinate system
class TreeDistance:

    def __init__(self,
                 coord_system: CoordSystem,
                 pwmatrix: PwMatrix):

        self.coord_system = coord_system
        self.pwmatrix = pwmatrix

    def __call__(self, a: Sample, b: Sample):
        x = np.array([self.pwmatrix[a, c] for c in self.coord_system.values()])
        y = np.array([self.pwmatrix[b, c] for c in self.coord_system.values()])
        return euclidean(x, y)

    @property
    def samples(self) -> Sequence[Any]:
        return self.pwmatrix.sample_map.samples


class VpTree(BaseVpTree):

    def __init__(self, config: Config, *args, **kwargs):
        super(VpTree, self).__init__(*args, **kwargs)
        self.config = config

    def save(self):
        config = self.config
        del self.config

        joblib.dump(self, config.vptree_path)

        self.config = config

    @staticmethod
    def load(config: Config):
        vptree = joblib.load(config.vptree_path)
        vptree.config = config
        return vptree

    @staticmethod
    @measure_time(enabled=True)
    def build(config: Config, tree_distance: Callable):
        return VpTree(config,
                      list(tree_distance.samples),
                      tree_distance)

    @measure_time(enabled=True)
    def add_samples(self,
                    samples: Sequence[Sample],
                    tree_distance: Callable):
        for sample_file in samples:
            self.add_sample(sample_file, tree_distance)

    def add_sample(self,
                   sample: Sample,
                   tree_distance: Callable):
        tree_distance.pwmatrix.add_sample(sample)
        self.insert(sample, tree_distance)
