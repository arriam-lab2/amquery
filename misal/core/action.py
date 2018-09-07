import operator as op
import inspect
from functools import partial
from inspect import signature
from typing import Callable, List, Tuple, Optional
from collections import OrderedDict

from fn.func import curried


__all__ = ['toaction', 'argument', 'Action']


VARARGS = frozenset(
    [inspect.Parameter.VAR_POSITIONAL,
     inspect.Parameter.VAR_KEYWORD]
)
EMPTY = inspect.Parameter.empty


class Action:

    def __init__(self, name: str, f: Callable,
                 argdocs: Optional[List[Tuple[str, str]]]=None,
                 description: Optional[str]=None, save: bool=False):
        # validate name
        # TODO should name be a valid Python identifier?
        # TODO should save be True by default?
        if not isinstance(name, str):
            raise ValueError(f'name is not a string')
        self._name = name

        # validate the callable
        arguments = signature(f).parameters
        if any(arg.kind in VARARGS for arg in arguments.values()):
            raise ValueError(f'action {name} has variadic arguments')
        self._action = f

        # validate the docs
        if argdocs is None:
            self._argdocs = OrderedDict((arg, '') for arg in arguments)
        else:
            documented_args = dict(argdocs)
            missing = set(arguments) - set(documented_args)
            unexpected = set(documented_args) - set(arguments)
            if missing:
                raise ValueError(f'missing docs for [{", ".join(missing)}]')
            if unexpected:
                raise ValueError(f'unexpected args [{", ".join(unexpected)}]')
            # align documentation
            self._argdocs = OrderedDict(
                (arg, documented_args[arg]) for arg in arguments
            )
        self._description = description or ''
        self._save = bool(save)

    def __call__(self, *args):
        if len(args) > len(self.arguments):
            raise TypeError(
                f'action {self.name} takes {len(self.arguments)} '
                f'positional arguments, but {len(args)} were given'
            )
        # execute underlying action if its signature is fulfilled
        if len(args) == len(self.arguments):
            return self.action(*args)
        # otherwise, curry the action
        f = partial(self.action, *args)
        curried_docs = self.arguments[len(args):]
        return type(self)(self.name, f, curried_docs, self.description, self.save)

    def __str__(self):
        arguments = list(signature(self.action).parameters.items())
        formatted_signature = [
            name if arg.annotation is EMPTY else f'{name}: {arg.annotation.__name__}'
            for name, arg in arguments
        ]
        return f'{self.name}({", ".join(formatted_signature)})'

    @property
    def arguments(self) -> List[Tuple[str, str]]:
        return list(self._argdocs.items())

    @property
    def description(self) -> str:
        return self._description

    @property
    def save(self) -> bool:
        return self._save

    @property
    def name(self) -> str:
        return self._name

    @property
    def action(self) -> Callable:
        return self._action


def toaction(save: bool, name: str=None, description: str=None):

    def decorator(f):
        if isinstance(f, Action):
            raise ValueError("Can't wrap an Action")
        action_name = f.__name__ if name is None else name
        return Action(action_name, f, None, description, save)

    return decorator


# TODO add type converters
def argument(name: str, documentation: str):

    def decorator(action: Action):
        if not isinstance(action, Action):
            raise ValueError(
                f'trying to specify argument {name} on a non-Action instance'
            )
        # retrieve action_'s content
        action_name = action.name
        f = action.action
        argdocs = action.arguments
        description = action.description
        save = action.save
        # check argument
        if name not in map(op.itemgetter(0), argdocs):
            raise ValueError(
                f'action {action.name} does not have argument {name}'
            )
        # update documentation
        new_docs = [(arg, doc) if arg != name else (name, documentation)
                    for arg, doc in argdocs]
        return Action(action_name, f, new_docs, description, save)

    return decorator


if __name__ == '__main__':
    raise RuntimeError
