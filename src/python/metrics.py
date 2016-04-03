from collections import defaultdict
import numpy as np
import random
import time


def hash_to_set(x: defaultdict) -> set:
    return set(x.values())


# Jaccard index of similarity
def jaccard(hx: defaultdict, hy: defaultdict) -> float:
    x = hash_to_set(hx)
    y = hash_to_set(hy)
    intersection = len(set.intersection(x, y))
    union = len(x) + len(y) - intersection
    return 1 - (intersection / float(union))


def generalized_jaccard(hx: defaultdict, hy: defaultdict) -> float:
    x, y = normalize(hx, hy)
    l1 = [min(a, b) for a, b in zip(x, y)]
    l2 = [max(a, b) for a, b in zip(x, y)]
    return 1 - sum(l1) / sum(l2)


def normalize(hx: defaultdict, hy: defaultdict) -> tuple:
    key_union = hx.copy()
    key_union.update(hy)

    x = np.array([hx[key] for key in key_union])
    y = np.array([hy[key] for key in key_union])

    return x / sum(x), y / sum(y)


# Bray-Curtis dissimilarity
def bray_curtis(hx: defaultdict, hy: defaultdict) -> float:
    x, y = normalize(hx, hy)
    return abs(x - y).sum() / abs(x + y).sum()


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
    t1 = defaultdict(int)
    t2 = defaultdict(int)

    random.seed(42)
    N = 50000
    for x in range(N):
        t1[x] = random.randint(1, 100)
        t2[x] = random.randint(1, 100)

    start = time.time()

    print(jaccard(t1, t2))
    print(generalized_jaccard(t1, t2))
    print(JSD(t1, t2))
    print(bray_curtis(t1, t2))

    end = time.time()
    print("Time: " + str(end - start))
