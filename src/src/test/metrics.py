from ..lib.metrics import *
import random
import time

# TODO create normal unit-test

print("metrics test: ", end="")

t1 = Counter()
t2 = Counter()

random.seed(42)
N = 50000
for x in range(N):
    t1[x] = random.randint(1, 100)
    t2[x] = random.randint(1, 100)


jcd = jaccard(t1, t2)
gjcd = generalized_jaccard(t1, t2)
jsdd = jsd(t1, t2)
bc = bray_curtis(t1, t2)

print("passed")
