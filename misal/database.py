from typing import TypeVar, Generic, Container, Sized, Callable, Tuple, Mapping, Union, Iterable, Sequence, Any
from itertools import filterfalse
from frozendict import frozendict
import operator as op
import importlib
import abc
import inspect
import keyword

from fn import F


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


Loader = Callable[['Database', Mapping], A]
Preprocessor = Callable[[Tuple[str]], A]
Transform = Callable[[A], B]
Distance = Callable[[A, A], float]


class Table(Sized, Container, Generic[A, B], metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def write(self, label: A, value: B) -> None:
        """
        Add something to the Table
        :param label:
        :param value:
        :return:
        """
        pass

    @abc.abstractmethod
    def read(self, label: A) -> B:
        """
        Read value from the table
        :param label:
        :return:
        """
        pass

    @abc.abstractmethod
    def flush(self):
        """
        Save all inserted values to the disk
        :return:
        """
        pass

    @abc.abstractmethod
    def __enter__(self) -> 'Table':
        pass

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class QueryTable(Table, Generic[A, B], metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def query(self, request: Mapping) -> Iterable[Tuple[A, B]]:
        pass


class Database(Generic[A, B]):

    def __init__(self,
                 preprocessor: Tuple[Loader[Preprocessor[A]], Mapping],
                 transform: Tuple[Loader[Transform[A, B]], Mapping],
                 distance: Tuple[Loader[Distance[B]], Mapping],
                 index: Tuple[Loader, Mapping],
                 ptable: Tuple[Loader[Table[int, A]], Mapping],
                 ttable: Tuple[Loader[Table[int, B]], Mapping],
                 mtable: Tuple[Loader[QueryTable[int, Mapping]], Mapping],
                 **custom_entries):
        # make sure all custom identifies are fine
        bad_iden = list(filterfalse(isidentifier, custom_entries.keys()))
        if bad_iden:
            raise ValueError(f'invalid identifiers: {bad_iden}')
        self._entries = frozendict(
            preprocessor=preprocessor,
            transform=transform,
            distance=distance,
            index=index,
            ptable=ptable,
            ttable=ttable,
            mtable=mtable,
            **custom_entries
        )
        # make sure entries pack valid loaders and argument Mappings
        bad_entries = [iden for iden, item in self._entries.items() if not
                       (len(item) == 2 and isloader(item[0])
                        and isinstance(item[1], Mapping))]
        if bad_entries:
            raise ValueError(f'invalid entries: {bad_entries}')

        self._loaded = {}

    def __getattr__(self, entry: str) -> Any:
        pass
    #     if entry not in self._loaders:
    #         raise AttributeError('no entry named {}'.format(entry))
    #     # uninvoked dependencies are False, loading dependencies are None,
    #     # loaded dependencies are True
    #     if self._status[entry] is None:
    #         raise RuntimeError("'{}' was accessed while loading".format(entry))
    #     if not self._status[entry]:
    #         self._activate_entry(entry)
    #     return self._entries[entry]

    @property
    def preprocessor(self) -> Preprocessor[A]:
        return self.__getattr__('preprocessor')

    @property
    def transform(self) -> Transform[A, B]:
        return self.__getattr__('transform')

    @property
    def distance(self) -> Distance[B]:
        return self.__getattr__('distance')

    def add(self, samples: Iterable[Tuple[Tuple[str], Mapping]]):
        pass

    def query(self, k: int,
              query: Union[Sequence[Tuple[str]], Sequence[int], Mapping]) \
            -> Iterable[Tuple[int, Mapping]]:
        pass

    def save(self):
        pass

    @classmethod
    def load(cls, spec):
        pass


def isloader(loader: A) -> bool:
    """
    Check whether `loader` satisfies basic properties of a Loader:
        1. it's a Callable
        2. it has exactly two arguments: a Database instance and a Mapping
        3. it is importable (i.e. is bound to the global namespace of an
           importable module)
    :param loader: a function to validate
    :return:
    """

    def checksignature(l: Callable) -> bool:
        parameters = inspect.signature(l).parameters
        if not len(parameters) == 2:
            return False
        first, second = parameters.values()
        return (issubclass(first.annotation, Database) and
                issubclass(second.annotation, Mapping))

    return callable(loader) and checksignature(loader) and importable(loader)


def importable(item) -> bool:
    """
    Check whether 'item' is accessible from its module's global namespace under
    'item.__name__'.
    :param item:
    :return:
    """
    try:
        module = importlib.import_module(inspect.getmodule(item).__name__)
        assert getattr(module, item.__name__) is item
    except (AssertionError, ImportError, ValueError, AttributeError):
        return False
    return True


def isidentifier(name: str) -> bool:
    """
    Determines if string is valid Python identifier.
    """
    if not isinstance(name, str):
        raise TypeError("expected str, but got {!r}".format(type(name)))
    return name.isidentifier() and not keyword.iskeyword(name)


if __name__ == '__main__':
    raise RuntimeError
