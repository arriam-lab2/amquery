import warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)


# Jenson-Shanon divergence
def jsd(x_distr: np.array,
        y_distr: np.array) -> float:

    x = x_distr / sum(x_distr)
    y = y_distr / sum(y_distr)

    print(len(x), len(y))

    z = x + y
    d1 = x * np.log2(2 * x / z)
    d2 = y * np.log2(2 * y / z)
    d1[np.isnan(d1)] = 0
    d2[np.isnan(d2)] = 0
    return np.sqrt(0.5 * np.sum(d1 + d2))


distances = {'jsd': jsd}
