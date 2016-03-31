from collections import defaultdict
import numpy as np


def hash_to_set(x: defaultdict) -> set:
    return set(x.values())


# Jaccard index of similarity
def jaccard(hx: defaultdict, hy: defaultdict) -> float:
    x = hash_to_set(hx)
    y = hash_to_set(hy)
    intersection = len(set.intersection(x, y))
    union = len(x) + len(y) - intersection
    return 1 - (intersection / float(union))


def normalize(hx: defaultdict, hy: defaultdict) -> float:
    key_union = hx.copy()
    key_union.update(hy)

    x = np.array([hx[key] for key in key_union])
    y = np.array([hy[key] for key in key_union])

    x = x / sum(x)
    y = y / sum(y)

    return x, y


# Bray-Curtis dissimilarity
def bray_curtis(hx: defaultdict, hy: defaultdict) -> float:
    x, y = normalize(hx, hy)
    return abs(x - y).sum() / abs(x + y).sum()
    # return dist.braycurtis(x, y)


# Jenson-Shanon divergence
def JSD(hx: defaultdict, hy: defaultdict) -> float:
    x, y = normalize(hx, hy)

    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    z = x + y
    d1 = x * np.log2(2 * x / z)
    d2 = y * np.log2(2 * y / z)
    d1[np.isnan(d1)] = 0
    d2[np.isnan(d2)] = 0
    return np.sqrt(0.5 * np.sum(d1 + d2))


if __name__ == "__main__":
    t1 = defaultdict(int, {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7})
    t2 = defaultdict(int, {1: 1, 13: 9, 5: 5, 16: 3, 7: 10})
    t3 = defaultdict(int, {1: 1, 2: 2, 3: 2, 4: 4, 5: 5, 6: 6, 7: 8})

    import random
    random.seed(42)
    N = 500000
    [t1.update({random.randint(1, N): x}) for x in range(N)]
    [t3.update({random.randint(1, N): x}) for x in range(N)]

    from time import time
    start = time()

#   res = jaccard(t1, t3)
#   res = JSD(t1, t3)
    res = bray_curtis(t1, t3)

    end = time()
    print("Time: " + str(end - start))
    print(res)
