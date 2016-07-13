import random

from ..lib.dist import kmerize_samples


print("dist test: ", end="")

ids = ["1", "2"]
samples = {}
for id in ids:
    samples[id] = ["".join(random.choice("ATGC") for _ in range(20))
                   for _ in range(10)]


kmerized = kmerize_samples(samples, 10)

for id in ids:
    assert id in kmerized.keys()
    assert len(kmerized[id]) > 0


print("passed")
