from typing import Iterable, List, Tuple

from misal.core import State
from misal.core.action import Action


class Actions(Action):

    def __call__(self) -> str:
        """
        Return formatted documentation for other functions
        :return:
        """
        pass

    @property
    def documentation(self) -> List[Tuple[str, str]]:
        return []

    @property
    def save(self) -> bool:
        return False

    @property
    def name(self) -> str:
        return 'actions'


class Help(Action):

    def __call__(self, *args, **kwargs):
        pass

    @property
    def documentation(self) -> List[Tuple[str, str]]:
        pass

    @property
    def save(self) -> bool:
        return False

    @property
    def name(self) -> str:
        pass


class Server:

    def __init__(self, port: int, state: State, actions: Iterable[Action]):
        # TODO should we run on something else but localhost?
        pass


if __name__ == '__main__':
    raise RuntimeError
