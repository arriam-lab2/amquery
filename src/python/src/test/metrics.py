from ..lib.metrics import *
import random
import time


# TODO create normal unit-test
t1 = Counter()
t2 = Counter()

random.seed(42)
N = 50000
for x in range(N):
    t1[x] = random.randint(1, 100)
    t2[x] = random.randint(1, 100)

start = time.time()

print(jaccard(t1, t2))
print(generalized_jaccard(t1, t2))
print(jsd(t1, t2))
print(bray_curtis(t1, t2))

end = time.time()
print("Time: " + str(end - start))
