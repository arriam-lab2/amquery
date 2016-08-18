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
from lib.kmerize.sample_map import SampleMap


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
        print("INSERT", point)
        if self.size == 0:
            self.vp = points
        else:
            print("MEDIAN", self.median)
            x = self.func(point, self.vp)
            y = self.median
            print(x, "VS. ", y)
            if x <= y:
                if not self.left:
                    self.left = BaseVpTree([point], self.func)
                else:
                    self.left.insert(point)
            else:
                if not self.right:
                    self.right = BaseVpTree([point], self.func)
                else:
                    self.right.insert(point)

        self.size += 1


class Distance:
    def __init__(self,
                 pwmatrix: PwMatrix):
        self.pwmatrix = pwmatrix

    def __call__(self, a: TreePoint, b: TreePoint):
        return self.pwmatrix[a, b]


def euclidean(a: np.ndarray, b: np.ndarray):
    return np.linalg.norm(a - b)


# Euclidean distance in a proper coordinate system
class TreeDistance:
    def __init__(self,
                 coord_system: CoordSystem,
                 pwmatrix: PwMatrix):

        self.coord_system = coord_system
        self.pwmatrix = pwmatrix

    def __call__(self, a: TreePoint, b: TreePoint):
        x = np.array([self.pwmatrix[a, c] for c in self.coord_system])
        y = np.array([self.pwmatrix[b, c] for c in self.coord_system])
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
        tree_distance = TreeDistance(coord_system, pwmatrix)

        #if not config.temp.quiet:
        #   print("Building a vp-tree...")

        vptree = VpTree(config, list(pwmatrix.labels), tree_distance)
        return vptree

    def add(self, input_files: List[str]):
        for sample in input_files:
            print(sample)
            self.insert(sample)
