
from tqdm import tqdm
import multiprocessing as mp
import time


def progress_bar(result, queue: mp.Queue, size: int):
    # progress bar loop
    with tqdm(total=size) as pbar:
        prev = 0

        while not result.ready():
            size = queue.qsize()
            k = size - prev
            if k > 0:
                pbar.update(k)
                prev = size
            time.sleep(1)

        k = queue.qsize() - prev
        if k > 0:
            pbar.update(k)

    return result
