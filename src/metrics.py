from __future__ import division

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
    xk = hx.keys()
    xv = np.array(hx.values())
    xv = xv / sum(xv)
    for (key, value) in zip(xk, xv):
        hx[key] = value


# Jenson-Shanon divergence
def JSD(hx, hy):
    x = hx
    y = hy
    prepare(x, y)
    x = sorted(x.items())
    y = sorted(y.items())

    import warnings

    warnings.filterwarnings("ignore", category = RuntimeWarning)
    x = np.array(hx.values())
    y = np.array(hy.values())

    d1 = x * np.log2(2*x/(x+y))
    d2 = y * np.log2(2*y/(x+y))
    d1[np.isnan(d1)] = 0
    d2[np.isnan(d2)] = 0
    return np.sqrt(0.5 * np.sum(d1 + d2))


if __name__ == "__main__":
    t1 = {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7}
    t2 = {1:1, 13:9, 5:5, 16:3, 7:10}
    t3 = {1:1, 2:2, 3:2, 4:4, 5:5, 6:6, 7:8}

    [t1.update({2*x: x}) for x in xrange(10000)]
    [t3.update({x: x}) for x in xrange(10000)]

    #import profile
    #profile.run('j = JSD(t1, t3)')
    #print(j)
