import time
from multiprocessing import Pool, Manager
from tqdm import tqdm


def play_function(a, b):
    time.sleep(0.5)  # mock work
    q.put(a)
    return i

p = Pool()
m = Manager()
q = m.Queue()

n = 20
inputs = range(n)
args = [(i, q) for i in inputs]
result = p.map_async(play_function, args)

prev = 0

# monitor loop
with tqdm(total=n) as pbar:
    while not result.ready():
        size = q.qsize()
        k = size - prev
        if k > 0:
            pbar.update(k)
            prev = size
        time.sleep(0.5)

    k = q.qsize() - prev
    if k > 0:
        pbar.update(k)


print()
outputs = result.get()

if __name__=="__main__":
    pass
