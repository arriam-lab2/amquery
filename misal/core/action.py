import operator as op
import inspect
from inspect import signature
from typing import Callable, List, Tuple, Optional
from collections import OrderedDict

from fn.func import curried


__all__ = ['action', 'argument', 'Action']


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
            docummented_args = dict(docs)
            missing = set(arguments) - set(docummented_args)
            unexpected = set(docummented_args) - set(arguments)
            if missing:
                raise ValueError(f'missing docs for [{", ".join(missing)}]')
            if unexpected:
                raise ValueError(f'unexpected args [{", ".join(unexpected)}]')
            # align documentation
            self._docs = OrderedDict(
                (arg, docummented_args[arg]) for arg in arguments
            )

        self._save = bool(save)

    def __call__(self, *args):
        # # align arguments
        # args_ = [(arg, val) for (arg, _), val in zip(self.documentation, args)]
        # repeated = [arg for (arg, _) in args_ if arg in kwargs]
        # if any(repeated):
        #     raise TypeError(
        #         f'action {self.name} got multiple values for arguments '
        #         f'[{", ".join(repeated)}]'
        #     )
        # unexpected = [kwarg for kwarg in self._docs if kwarg not in self._docs]
        # if any(unexpected):
        #     raise TypeError(
        #         f'action {self.name} got unexpected keyword arguments '
        #         f'[{", ".join(unexpected)}]'
        #     )
        if len(args) > len(self.documentation):
            raise TypeError(
                f'action {self.name} takes {len(self.documentation)} '
                f'positional arguments, but {len(args)} were given'
            )
        # execute underlying action if its signature is fulfilled
        if len(args) == len(self.documentation):
            return self.action(*args)
        # otherwise, curry the action
        f = self.action(*args)
        truncated_docs = self.documentation[len(args):]
        return type(self)(self.name, f, truncated_docs, self.save)

    def __str__(self):
        return f'{self.name}({", ".join(map(op.itemgetter(0), self._docs))})'

    @property
    def documentation(self) -> List[Tuple[str, str]]:
        return list(self._docs.items())

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
