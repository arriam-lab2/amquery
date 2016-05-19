import numpy as np
from scipy.spatial.distance import correlation

from ..lib import pwcomp


# TODO write a unit-test


fn = correlation
data = np.repeat(np.arange(100), 1000).reshape((100, 1000)).T
print(pwcomp.pwmatrix(fn, data, dist=False))