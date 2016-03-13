#from __future__ import division
from collections import defaultdict

def hash_to_set(x):
    return set(x.values())

# Jaccard index of similarity
def jaccard(hx, hy):
    x = hash_to_set(hx)
    y = hash_to_set(hy)
    intersection = len(set.intersection(x, y))
    union = len(set.union(x, y))
    return 1 - (intersection / float(union))

# Bray-Curtis dissimilarity
#def bray_curtis(x, y):
#intersection = len(set.intersection(x, y))
#pass

import numpy as np

def prepare(hx, hy):
    extends(hx, hy)
    extends(hy, hx)
    norm(hx)
    norm(hy)


def extends(hx, hy):
    rest_keys = [key for key in hx if key not in hy]
    for key in rest_keys:
        hy[key] = 0


def norm(hx):
    xk = np.array([k for k in hx.keys()])
    xv = np.array([v for v in hx.values()])
    xv = xv / sum(xv)
    for (key, value) in zip(xk, xv):
        hx[key] = value



# Jenson-Shanon divergence    
def JSD(hx: dict, hy: dict) -> float:
    x = defaultdict(float, hx)
    y = defaultdict(float, hy)

    key_union = x.copy()
    key_union.update(y)

    x_array = np.array([x[key] for key in key_union])
    y_array = np.array([y[key] for key in key_union])

    x_array = x_array / sum(x_array)
    y_array = y_array / sum(y_array)

    x = x_array
    y = y_array

    import warnings
    warnings.filterwarnings("ignore", category = RuntimeWarning)

    d1 = x * np.log2(2 * x / (x + y))
    d2 = y * np.log2(2 * y / (x + y))
    d1[np.isnan(d1)] = 0
    d2[np.isnan(d2)] = 0
    return np.sqrt(0.5 * np.sum(d1 + d2))



if __name__ == "__main__":
    t1 = {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7}
    t2 = {1:1, 13:9, 5:5, 16:3, 7:10}
    t3 = {1:1, 2:2, 3:2, 4:4, 5:5, 6:6, 7:8}
    
    from time import time
    start = time()

    import random
    random.seed(42)
    #N = 1000000
    #[t1.update({random.randint(1, N): x}) for x in range(N)]
    #[t3.update({random.randint(1, N): x}) for x in range(N)]

    j = JSD(t1, t3)
    print(j)

    end = time()
    print("Time: " + str(end - start))


