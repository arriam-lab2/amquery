from typing import List, Tuple

from misal.core.config import Action


class Add(Action):

    def __init__(self, metadata, preprocessed, index):
        pass

    def __call__(self, *args, **kwargs):
        pass

    @property
    def documentation(self) -> List[Tuple[str, str]]:
        return []

    @property
    def save(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return 'add'


class Search(Action):

    def __init__(self, preprocessed, index):
        pass

    def __call__(self, *args, **kwargs):
        pass

    @property
    def documentation(self) -> List[Tuple[str, str]]:
        return []

    @property
    def save(self) -> bool:
        return False

    @property
    def name(self) -> str:
        return 'search'


if __name__ == '__main__':
    raise RuntimeError
