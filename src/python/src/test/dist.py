import random

from ..lib.dist import kmerize_samples


samples = {
    "1": ["".join(
        random.choice("ATGC") for _ in range(100)) for _ in range(10)],
    "2": ["".join(
        random.choice("ATGC") for _ in range(100)) for _ in range(10)]
}


print(kmerize_samples(samples, 10))
