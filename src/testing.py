#!/usr/bin/env python3

import numpy as np
import random
import os
import src.lib.vptree as vptree


def _precision_recall(y_true, y_pred):
    precision = 0
    recall = 0

    for y in y_pred:
        if y in y_true:
            precision += 1

    for y in y_true:
        if y in y_pred:
            recall += 1

    precision = precision / len(y_pred)
    recall = recall / len(y_true)
    f1 = 0
    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    return precision, recall, f1


def best(solutions, k, exclude_labels):
    solutions = sorted(solutions, key=lambda tup: tup[1])
    solutions = [(x, y) for x, y in solutions if x not in exclude_labels]
    return solutions[:k]


def test(config, proxy, dist_tree, train_labels, labels, pwmatrix, k_values):
    test_labels = list(set(labels) - set(train_labels))
    dist_matrix = dist_tree.func.matrix
    dist_labels_map = dist_tree.func.map

    result = []
    for k in k_values:
        stats = []
        for label in test_labels:
            y_pred = proxy(label, k)
            pred_values = [(y,
                           list(np.array(dist_matrix[dist_labels_map[y]])[0]))
                           for y in y_pred]
            pred_values = [(p[0], p[1][dist_labels_map[label]])
                           for p in pred_values]
            pred_values = best(pred_values, k, test_labels + [label])

            true_values = list(zip(labels,
                                   np.array(pwmatrix[labels.index(label)])[0]))
            true_values = best(true_values, k, test_labels + [label])

            y_pred = [x for x, _ in pred_values]
            y_true = [x for x, _ in true_values]
            precision, recall, f1 = _precision_recall(y_true, y_pred)
            stats.append([precision, recall, f1])

        stats = np.array(stats, dtype=np.float)
        stats = np.nanmean(stats, axis=0)
        result.append(list(stats))

    return result


class RandomNeighbors:
    def __init__(self, labels):
        self.labels = labels

    def __call__(self, k):
        return random.sample(self.labels, k)


class DistProxy:
    def __init__(self, dist_tree):
        self.tree = dist_tree

    def __call__(self, label, k):
        subtree = vptree.nearest_neighbors(self.tree, label, k)
        return subtree.dfs()


class BaselineProxy:
    def __init__(self, labels):
        self.rn = RandomNeighbors(labels)

    def __call__(self, label, k):
        return self.rn(k)


def dist(config, dist_tree, train_labels, labels, pwmatrix,
         k_values, output_file):
    result = test(config, DistProxy(dist_tree), dist_tree, train_labels,
                  labels, pwmatrix, k_values)

    output_file = os.path.join(config.working_directory, output_file)
    with open(output_file, 'w') as f:
        f.write('\n'.join(str(f1) for p, r, f1 in result))


def baseline(config, dist_tree, train_labels, labels, pwmatrix, k_values):
    result = test(config, BaselineProxy(train_labels), dist_tree, train_labels,
                  labels, pwmatrix, k_values)

    output_file = os.path.join(config.working_directory,
                               'baseline.txt')
    with open(output_file, 'w') as f:
        f.write('\n'.join(str(f1) for p, r, f1 in result))


if __name__ == "__main__":
    pass
