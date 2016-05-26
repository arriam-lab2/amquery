#!/usr/bin/env python3

import numpy as np
import random
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


def run(config, dist_tree, train_labels, unif_tree, k):
    labels = dist_tree.func.map.keys()
    test_labels = list(set(labels) - set(train_labels))

    results = []
    for label in test_labels:
        dist_subt = vptree.nearest_neighbors(dist_tree, label, k)
        y_pred = dist_subt.dfs()

        unif_subt = vptree.nearest_neighbors(unif_tree, label, k)
        y_true = unif_subt.dfs()

        precision, recall, f1 = _precision_recall(y_true, y_pred)
        # print(precision, recall, f1)
        results.append([precision, recall, f1])

    results = np.array(results, dtype=np.float)
    results = np.mean(results, axis=0)
    # print(results)
    return results


class RandomNeighbors:
    def __init__(self, labels):
        self.labels = labels

    def __call__(self, k):
        return random.sample(self.labels, k)


def baseline(config, dist_tree, train_labels, unif_tree, k):
    labels = dist_tree.func.map.keys()
    test_labels = list(set(labels) - set(train_labels))

    rn = RandomNeighbors(labels)
    results = []
    for label in test_labels:
        y_pred = rn(k)

        unif_subt = vptree.nearest_neighbors(unif_tree, label, k)
        y_true = unif_subt.dfs()

        precision, recall, f1 = _precision_recall(y_true, y_pred)
        results.append([precision, recall, f1])

    results = np.array(results, dtype=np.float)
    results = np.nanmean(results, axis=0)
    # print(results)
    return results


if __name__ == "__main__":
    pass
