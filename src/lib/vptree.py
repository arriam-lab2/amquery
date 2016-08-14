#!/usr/bin/env python3

import random
import numpy as np
import itertools
import pickle
import os
from typing import Callable, Mapping, List


class Point:
    pass


class Sample(Point):
    def __init__(self, name: str):
        self.__super__()
        self.name = name


class Distance:
    def __init__(self, labels_map: Mapping, matrix: np.ndarray):
        self.map = labels_map
        self.matrix = matrix

    def __call__(self, a: Point, b: Point):
        return self.matrix[self.map[a], self.map[b]]


def euclidean(a: np.ndarray, b: np.ndarray):
    return np.linalg.norm(a - b)


# Distance in a proper coordinate system
class CsDistance:
    def __init__(self, labels_map: Mapping, coord_system: List[str],
                 matrix: np.ndarray):
        self.map = labels_map
        self.matrix = matrix
        self.coord_system = coord_system
        self.dist = Distance(labels_map, matrix)

    def __call__(self, a: Point, b: Point):
        x = np.array([self.dist(a, c) for c in self.coord_system])
        y = np.array([self.dist(b, c) for c in self.coord_system])
        return euclidean(x, y)



# Vantage-point tree
class VpTree:
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
                self.left = VpTree(leftside, func)
                self.size += self.left.size
            if len(rightside) > 0:
                self.right = VpTree(rightside, func)
                self.size += self.right.size

    # depth-first search
    def dfs(self) -> list:
        result = []
        if self.left:
            result.extend(self.left.dfs())
        if self.right:
            result.extend(self.right.dfs())

        result.append(self.vp)
        return result


def nearest_neighbors(vptree: VpTree, x: Point, k: int) -> list:
    tree = vptree
    func = tree.func

    while tree.size > k:
        dist = func(tree.vp, x)
        if tree.median and dist <= tree.median:
            if tree.left.size < k:
                return tree
            tree = tree.left
        elif tree.median and dist > tree.median:
            if tree.right.size < k:
                return tree
            tree = tree.right
        else:
            return tree

    return tree


def build(config, distance, labels, pwmatrix):
    vptree = VpTree(labels, distance)

    output_file = config.get_vptree_path()
    pickle.dump(vptree, open(output_file, "wb"))

    return vptree


def dist(config, coord_system, labels, pwmatrix):
    labels_map = dict(zip(labels, range(len(labels))))
    distance = CsDistance(labels_map, coord_system, pwmatrix)
    return build(config, distance, labels, pwmatrix)
