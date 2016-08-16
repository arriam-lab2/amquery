from typing import List

from vptree import BaseVpTree, TreePoint


def nearest_neighbors(vptree: BaseVpTree,
                      x: TreePoint,
                      k: int) -> List[TreePoint]:
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
def dfs(self) -> list:
    result = []
    if self.left:
        result.extend(self.left.dfs())
    if self.right:
        result.extend(self.right.dfs())

    result.append(self.vp)
    return result
