import numpy as np
from scipy.spatial.distance import correlation

from lib import pwcomp


# TODO write a unit-test

print("pwcomp test: ", end="")

fn = correlation
data = np.repeat(np.arange(100), 100).reshape((100, 100)).T
res = pwcomp.pwmatrix(fn, data)

print("passed")
