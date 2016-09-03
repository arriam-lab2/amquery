import warnings
import numpy as np
from collections import Counter
from typing import Tuple, Any

warnings.filterwarnings("ignore", category=RuntimeWarning)


def normalize(hx: Counter, hy: Counter) -> Tuple[Any]:
    key_union = hx.keys() | hy.keys()

    x = np.array([hx[key] for key in key_union])
    y = np.array([hy[key] for key in key_union])

    return x / np.sum(x), y / np.sum(y)


# Jenson-Shanon divergence
def jsd(hx: Counter, hy: Counter) -> float:
    x, y = normalize(hx, hy)
    z = x + y

    d1 = x * np.log2(2 * x / z)
    d2 = y * np.log2(2 * y / z)

    d1[np.isnan(d1)] = 0
    d2[np.isnan(d2)] = 0
    return np.sqrt(0.5 * np.sum(d1 + d2))

distances = {'jsd': jsd}
