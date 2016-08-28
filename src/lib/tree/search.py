from typing import List, Any, Tuple
import numpy as np

from lib.tree.vptree import BaseVpTree


def _neighbor_subtree(vptree: BaseVpTree,
                      x: Any,
                      k: int) -> BaseVpTree:
    tree = vptree
    func = tree.func

    while tree.size > k:
        dist = func(tree.vp, x)
        if tree.median and dist <= tree.median:
            if tree.left.size < k:
                return tree
            tree = tree.left
        elif tree.median and dist > tree.median:
            if tree.right.size < k:
                return tree
            tree = tree.right
        else:
            return tree

    return tree


# depth-first search
def dfs(tree: BaseVpTree) -> List[Any]:
    result = []
    if tree.left:
        result.extend(dfs(tree.left))
    if tree.right:
        result.extend(dfs(tree.right))

    result.append(tree.vp)
    return result


def neighbors(vptree: BaseVpTree,
              x: Any,
              k: int) -> Tuple[np.array, np.array]:

    subtree = _neighbor_subtree(vptree, x, k)
    points = np.array(dfs(subtree))
    values = np.array([vptree.func(x, p) for p in points])
    points = points[values.argsort()]
    values = np.sort(values)
    return values[:k], points[:k]
