from typing import Iterable, List, Tuple

from misal.core import action, State


@action.action(save=False)
def help(actions: List[action.Action]) -> str:
    """
    Default action for documentation
    :param actions:
    :return:
    """
    pass


class Server:

    def __init__(self, port: int, state: State, actions: List[action.Action]):
        # TODO should we run on something else but localhost?
        pass


if __name__ == '__main__':
    raise RuntimeError
