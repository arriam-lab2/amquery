#!/usr/bin/env python3

import itertools
import random
import numpy as np
import pickle
from typing import Callable, Any, Sequence

from ..distance import PwMatrix
from ..coord_system import CoordSystem
from ..config import Config
from lib.kmerize.sample import Sample
from lib.kmerize.sample_map import SampleMap


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

    def insert(self, point: Any):
        if self.size == 0:
            self.vp = point
        else:
            distance_value = self.func(point, self.vp)
            if not self.median:
                self.median = distance_value

            if distance_value <= self.median:
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


class VpTree(BaseVpTree):
    def __init__(self, config: Config, *args, **kwargs):
        super(VpTree, self).__init__(*args, **kwargs)
        self.config = config

    def save(self):
        config = self.config
        del self.config

        pickle.dump(self, open(config.vptree_path, "wb"))
        self.pwmatrix.save()

        self.config = config

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

        tree_distance = TreeDistance(coord_system, pwmatrix)
        return VpTree(config,
                      list(pwmatrix.sample_map.samples),
                      tree_distance)

    def add_samples(self, samples: Sequence[Sample]):
        for sample_file in samples:
            self.add_sample(sample_file)

    def add_sample(self, sample: Sample):
        self.pwmatrix.add_sample(sample)
        self.insert(sample)

    @property
    def pwmatrix(self) -> PwMatrix:
        return self.func.pwmatrix

    @property
    def sample_map(self) -> SampleMap:
        return self.pwmatrix.sample_map
