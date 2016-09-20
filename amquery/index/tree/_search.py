from typing import Any, Tuple, Callable
import numpy as np
import queue

from amquery.index.tree import BaseVpTree


def _neighbors(tree: BaseVpTree,
               query_point: Any,
               k: int,
               tree_distance: Callable):
    tau = np.inf
    neighbors = queue.PriorityQueue()
    node_queue = queue.Queue()
    node_queue.put(tree)

    while not node_queue.empty():
        node = node_queue.get()
        if node:
            d = tree_distance(query_point, node.vp)

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
              query_point: Any,
              k: int,
              tree_distance: Callable) -> Tuple[np.array, np.array]:

    result = _neighbors(vptree, query_point, k, tree_distance)
    result = sorted([(-value, point) for value, point in result])
    values, points = zip(*result)
    return np.array(values), np.array(points)
