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

# Jenson-Shanon divergence
def JSD(x, y):
    import numpy as np
    import warnings

    warnings.filterwarnings("ignore", category = RuntimeWarning)
    x = np.array(x)
    y = np.array(y)
    d1 = x*np.log2(2*x/(x+y))
    d2 = y*np.log2(2*y/(x+y))
    d1[np.isnan(d1)] = 0
    d2[np.isnan(d2)] = 0
    return sqrt(0.5 * np.sum(d1 + d2))


