import abc
import importlib
import inspect
import keyword
from itertools import filterfalse
from typing import TypeVar, Generic, Container, Sized, Callable, Tuple, \
    Mapping, Union, Iterable, Sequence, Any, Optional, Dict, cast

from frozendict import frozendict

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


class Database(Sized, Generic[A, B]):

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
        self._entries: Mapping[str, Tuple[Loader, Mapping]] = frozendict(
            preprocessor=preprocessor,
            transform=transform,
            distance=distance,
            index=index,
            ptable=ptable,
            ttable=ttable,
            mtable=mtable,
            **custom_entries
        )
        # make sure entries pack valid loaders and parameter Mappings
        bad_entries = [iden for iden, item in self._entries.items() if not
                       (len(item) == 2 and isloader(item[0])
                        and isinstance(item[1], Mapping))]
        if bad_entries:
            raise ValueError(f'invalid entries: {bad_entries}')

        self._loaded: Dict[str, Optional[Any]] = {}

    def __getattr__(self, entry: str) -> Any:
        if entry not in self._entries:
            raise AttributeError(f'no entry named {entry!r}')
        if entry not in self._loaded:
            self._loaded[entry] = None
            loader, parameters = self._entries[entry]
            self._loaded[entry] = loader(self, parameters)
        # loading dependencies are None
        if self._loaded[entry] is None:
            raise RuntimeError(f'{entry!r} was accessed while loading, '
                               'which is a sign of circular dependencies')
        return self._loaded[entry]

    def __len__(self):
        return len(self.ttable)

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
        paths, metadata = zip(*samples)
        # TODO we might consider multiprocessing here
        preprocessed = list(map(self.preprocessor, paths))
        # TODO and multithreading here
        transformed = list(map(self.transform, preprocessed))
        # TODO we can use all these context-managers in parallel, but it'll
        # make error-handling more complicated
        with cast(Table, self.ptable) as ptable:
            for sample in preprocessed:
                ptable.write(len(ptable), sample)
        with cast(Table, self.ttable) as ttable:
            for sample in transformed:
                ttable.write(len(ttable), sample)
        with cast(QueryTable, self.mtable) as mtable:
            for meta in metadata:
                mtable.write(len(mtable), meta)

    def query(self, k: int,
              query: Union[Sequence[Tuple[str]], Sequence[int], Mapping]) \
            -> Iterable[Tuple[int, Mapping]]:
        raise NotImplementedError

    def save(self) -> Mapping[str, Tuple[str, Mapping[str, Any]]]:
        raise NotImplementedError

    @classmethod
    def load(cls, spec: Mapping[str, Tuple[str, Mapping[str, Any]]]) -> 'Database':
        raise NotImplementedError


def isloader(loader: A) -> bool:
    """
    Check whether `loader` satisfies basic properties of a Loader:
        1. it's a Callable
        2. it has exactly two arguments: a Database instance and a Mapping
        3. it is importable (i.e. is bound to the global namespace of an
           importable module)
    :param loader: a callable to validate
    :return:
    """

    def proper_signature(l: Callable) -> bool:
        parameters = inspect.signature(l).parameters
        if not len(parameters) == 2:
            return False
        first, second = parameters.values()
        return (issubclass(first.annotation, Database) and
                issubclass(second.annotation, Mapping))

    return callable(loader) and proper_signature(loader) and importable(loader)


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
        raise TypeError(f'expected str, but got {type(name)!r}')
    return name.isidentifier() and not keyword.iskeyword(name)


if __name__ == '__main__':
    raise RuntimeError
