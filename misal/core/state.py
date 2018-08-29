import abc
import contextlib
from typing import TypeVar, Iterable, Callable, Generic, NewType, overload

from oslash import Functor, Applicative


__all__ = ['State', 'Stateful']


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

SampleID = NewType('SampleID', int)

# TODO should we make this whole thing asynchronous?
# TODO wrap all function in curry


class Sample(Functor, Applicative, Generic[A], metaclass=abc.ABCMeta):

    def __init__(self, sid: SampleID, value: A):
        self._id = sid
        self._value = value

    @property
    def sid(self) -> SampleID:
        return self._id

    def __repr__(self):
        return f'{type(self)}({self.sid}, {self.value})'

    def map(self, fn: Callable[[A], B]) -> 'Sample':
        result = fn(self._value)
        return type(self)(self.sid, result)

    def apply(self, something: 'Sample') -> 'Sample':
        return something.map(self.value)


class Stateful(Generic[A], metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def save(self):
        pass

    @abc.abstractmethod
    def reset(self):
        pass

    @overload
    @abc.abstractmethod
    def register(self, value: A) -> Sample[A]:
        pass

    @overload
    @abc.abstractmethod
    def register(self, value: Sample[A]) -> Sample[A]:
        pass

    @abc.abstractmethod
    def register(self, value):
        pass


class State(contextlib.AbstractContextManager):

    def __init__(self, states: Iterable[Stateful]):
        self._states = tuple(states)
        self._persist = False

    def __call__(self, persist: bool) -> 'State':
        self._persist = persist
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # TODO handle exc_type and errors in state.commit() and state.drop()
        for state in self._states:
            if self._persist:
                state.save()
            state.reset()
        self._persist = False


if __name__ == '__main__':
    raise RuntimeError
