from collections import Counter
import warnings

import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)


def hash_to_set(x: Counter) -> set:
    return set(x.values())


def normalize(hx: Counter, hy: Counter) -> tuple:
    key_union = hx.keys() | hy.keys()

    x = np.array([hx[key] for key in key_union])
    y = np.array([hy[key] for key in key_union])

    return x / sum(x), y / sum(y)


# Jaccard index of similarity
def jaccard(hx: Counter, hy: Counter) -> float:
    x = hash_to_set(hx)
    y = hash_to_set(hy)
    intersection = len(x & y)
    union = len(x) + len(y) - intersection
    return 1 - (intersection / float(union))


def generalized_jaccard(hx: Counter, hy: Counter) -> float:
    x, y = normalize(hx, hy)
    l1 = [min(a, b) for a, b in zip(x, y)]
    l2 = [max(a, b) for a, b in zip(x, y)]
    return 1 - sum(l1) / sum(l2)


# Bray-Curtis dissimilarity
def bray_curtis(hx: Counter, hy: Counter) -> float:
    x, y = normalize(hx, hy)
    return abs(x - y).sum() / abs(x + y).sum()


# Jenson-Shanon divergence
def jsd(hx: Counter, hy: Counter) -> float:
    x, y = normalize(hx, hy)

    z = x + y
    d1 = x * np.log2(2 * x / z)
    d2 = y * np.log2(2 * y / z)
    d1[np.isnan(d1)] = 0
    d2[np.isnan(d2)] = 0
    return np.sqrt(0.5 * np.sum(d1 + d2))


distances = {'jaccard': jaccard, 'jsd': jsd, 'bc': bray_curtis,
             'gji': generalized_jaccard}
