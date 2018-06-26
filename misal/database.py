from typing import TypeVar, Generic, Container, Sized
import abc


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class Table(Sized, Container, Generic[A, B], metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def write(self, name: A, value: B) -> None:
        pass

    @abc.abstractmethod
    def read(self, name: A) -> B:
        pass

    @abc.abstractmethod
    def flush(self):
        pass

    @abc.abstractmethod
    def __enter__(self) -> 'Table':
        pass

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == '__main__':
    raise RuntimeError
