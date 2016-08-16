#!/usr/bin/env python3

import random
import numpy as np
import pickle
import os
from typing import Callable, Mapping, List

from ..distance import PwMatrix
from ..coord_system import CoordSystem
from ..config import Config
from ..metrics import distances


import numpy as np
import random
import itertools
from typing import Callable

class TreePoint:
    pass

class Sample(TreePoint):
    def __init__(self, name: str, *args, **kwargs):
        super(Sample, self).__init__(*args, **kwargs)
        self.name = name


# Vantage-point tree
class BaseVpTree:
    def __init__(self, points: np.array, func: Callable):
        self.func = func
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

            dists = map(self.func, points, itertools.repeat(self.vp))
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

    def insert(self, point):
        if len(points) == 0:
            self.vp = points
        else:
            if self.func(point, self.vp) <= self.median:
                self.left.insert(point)
            else:
                self.right.insert(point)

        self.size += 1


class Distance:
    def __init__(self,
                 dist_function: Callable,
                 precalc: PwMatrix):
        self.dist_function = dist_function
        self.map = dict(zip(precalc.labels, range(len(precalc.labels))))
        self.precalc = precalc

    def __call__(self, a: TreePoint, b: TreePoint):
        if a in self.precalc.labels and b in self.precalc.labels:
            return self.precalc.matrix[self.map[a], self.map[b]]
        else:
            raise NotImplementedError()


def euclidean(a: np.ndarray, b: np.ndarray):
    return np.linalg.norm(a - b)


# Euclidean distance in a proper coordinate system
class TreeDistance:
    def __init__(self,
                 dist_function: Callable,
                 coord_system: CoordSystem,
                 pwmatrix: PwMatrix):

        self.coord_system = coord_system
        self.dist = Distance(dist_function, pwmatrix)

    def __call__(self, a: TreePoint, b: TreePoint):
        x = np.array([self.dist(a, c) for c in self.coord_system])
        y = np.array([self.dist(b, c) for c in self.coord_system])
        return euclidean(x, y)


class VpTree(BaseVpTree):
    def __init__(self, config: Config, *args, **kwargs):
        super(VpTree, self).__init__(*args, **kwargs)
        self.config = config

    def save(self):
        config = self.config
        del self.config
        pickle.dump(self, open(config.vptree_path, "wb"))

    @staticmethod
    def load(config: Config):
        with open(config.vptree_path, 'rb') as f:
            vptree = pickle.load(f)
            vptree.config = config
            return vptree

    @staticmethod
    def build(config: Config,
              coord_system: CoordSystem = None,
              pwmatrix: PwMatrix = None):

        if not coord_system:
            coord_system = CoordSystem.load(config)

        if not pwmatrix:
            pwmatrix = PwMatrix.load(config)

        distance_func = distances[config.dist.func]
        tree_distance = TreeDistance(distance_func, coord_system, pwmatrix)

        #if not config.temp.quiet:
        #   print("Building a vp-tree...")

        vptree = VpTree(config, list(pwmatrix.labels), tree_distance)
        return vptree

    def add(self, input_files: List[str]):
        raise NotImplementedError()
