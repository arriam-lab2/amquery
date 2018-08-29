import operator as op
import inspect
from inspect import signature
from typing import Callable, List, Tuple, Optional

from fn.func import curried


VARARGS = frozenset(
    [inspect.Parameter.VAR_POSITIONAL,
     inspect.Parameter.VAR_KEYWORD]
)


class Action:

    def __init__(self, name: str, f: Callable,
                 docs: Optional[List[Tuple[str, str]]]=None,
                 save: bool=False):
        # validate name
        # TODO should name be a valid Python identifier?
        if not isinstance(name, str):
            raise ValueError(f'name is not a string')
        self._name = name

        # validate the callable
        arguments = signature(f).parameters
        if any(arg.kind in VARARGS for arg in arguments.values()):
            raise ValueError(f'action {name} has variadic arguments')
        self._action = curried(f)

        # validate the docs
        if docs is None:
            self._docs = [(arg, '') for arg in arguments]
        else:
            docummented_args = set(map(op.itemgetter(0), docs))
            missing = set(arguments) - docummented_args
            excessive = docummented_args - set(arguments)
            if missing:
                raise ValueError(f'missing docs for [{", ".join(missing)}]')
            if excessive:
                raise ValueError(f'nonexistent args [{", ".join(excessive)}]')
            self._docs = docs[:]

        self._save = bool(save)

    # TODO analyse signature
    # TODO implement currying

    def __call__(self, *args, **kwargs):
        # add currying logic
        # check arguments
        raise NotImplemented
        # return self._action(*args, **kwargs)

    def __str__(self):
        return f'{self.name}({", ".join(map(op.itemgetter(0), self._docs))})'

    @property
    def documentation(self) -> List[Tuple[str, str]]:
        return self._docs

    @property
    def save(self) -> bool:
        return self._save

    @property
    def name(self) -> str:
        return self._name

    @property
    def action(self) -> Callable:
        return self._action


def action(save: bool, name: str=None):

    def decorator(f):
        action_name = f.__name__ if name is None else name
        return Action(action_name, f, None, save)

    return decorator


def argument(name: str, description: str):

    def decorator(action_: Action):
        if not isinstance(action_, Action):
            raise ValueError(
                f'trying to specify argument {name} on a non-Action instance'
            )
        # retrieve action_'s content
        action_name = action_.name
        f = action_.action
        docs = action_.documentation
        save = action_.save
        # update documentation
        new_docs = [(arg, descr) if arg != name else (name, description)
                    for arg, descr in docs]
        return Action(action_name, f, new_docs, save)

    return decorator


if __name__ == '__main__':
    raise RuntimeError
