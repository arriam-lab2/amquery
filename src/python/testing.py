#!/usr/bin/env python3

import numpy as np
import random
import os
import python.vptree as vptree


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
    f1 = None
    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    return precision, recall, f1


def run(config, dist_tree, train_labels, unif_tree, k_values):
    labels = dist_tree.func.map.keys()
    test_labels = list(set(labels) - set(train_labels))

    result = []
    for k in k_values:
        stats = []
        for label in test_labels:
            dist_subt = vptree.nearest_neighbors(dist_tree, label, k)
            y_pred = dist_subt.dfs()

            unif_subt = vptree.nearest_neighbors(unif_tree, label, k)
            y_true = unif_subt.dfs()

            precision, recall, f1 = _precision_recall(y_true, y_pred)
            stats.append([precision, recall, f1])

        stats = np.array(stats, dtype=np.float)
        stats = np.nanmean(stats, axis=0)
        result.append(list(stats))

    output_file = os.path.join(config.working_directory,
                               'dist.txt')
    with open(output_file, 'w') as f:
        f.write('\n'.join(str(f1) for p, r, f1 in result))


class RandomNeighbors:
    def __init__(self, labels):
        self.labels = labels

    def __call__(self, k):
        return random.sample(self.labels, k)


def baseline(config, dist_tree, train_labels, unif_tree, k_values):
    labels = dist_tree.func.map.keys()
    test_labels = list(set(labels) - set(train_labels))

    rn = RandomNeighbors(labels)

    result = []
    for k in k_values:
        stats = []
        for label in test_labels:
            y_pred = rn(k)

            unif_subt = vptree.nearest_neighbors(unif_tree, label, k)
            y_true = unif_subt.dfs()

            precision, recall, f1 = _precision_recall(y_true, y_pred)
            stats.append([precision, recall, f1])

        stats = np.array(stats, dtype=np.float)
        stats = np.nanmean(stats, axis=0)
        result.append(list(stats))

    output_file = os.path.join(config.working_directory,
                               'baseline.txt')
    with open(output_file, 'w') as f:
        f.write('\n'.join(str(f1) for p, r, f1 in result))


if __name__ == "__main__":
    pass
