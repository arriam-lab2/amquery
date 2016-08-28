from typing import Any, Tuple
import numpy as np
import queue

from lib.tree.vptree import BaseVpTree


def _neighbors(tree: BaseVpTree, x: Any, k: int):
    tau = np.inf
    neighbors = queue.PriorityQueue()
    node_queue = queue.Queue()
    node_queue.put(tree)

    while not node_queue.empty():
        node = node_queue.get()
        if node:
            d = tree.func(x, node.vp)

            if len(neighbors.queue) < k:
                neighbors.put((-d, node.vp))
            elif d < tau:
                neighbors.put((-d, node.vp))
                if len(neighbors.queue) > k:
                    neighbors.get()

                tau, _ = neighbors.queue[0]
                tau *= -1

            if not node.median:
                continue

            if d < node.median:
                if d < node.median + tau:
                    node_queue.put(node.left)
                if d >= node.median - tau:
                    node_queue.put(node.right)
            else:
                if d < node.median + tau:
                    node_queue.put(node.left)
                if d >= node.median - tau:
                    node_queue.put(node.right)

    return neighbors.queue


def neighbors(vptree: BaseVpTree,
              x: Any,
              k: int) -> Tuple[np.array, np.array]:

    result = _neighbors(vptree, x, k)
    result = sorted([(-value, point) for value, point in result])
    values, points = zip(*result)
    return np.array(values), np.array(points)
