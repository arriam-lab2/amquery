import re
from collections import OrderedDict
from importlib import import_module
from typing import Mapping, Any, Iterable, Tuple

from fn import F
from simpleeval import EvalWithCompoundTypes

from misal.core.action import Action
from misal.core.state import State, Stateful


__all__ = ['parse']


DEFINITION = re.compile(
    '^let (?P<name>[A-Za-z][A-Za-z0-9_]+)\s+?=\s+?(?P<expr>.+)$'
)
EXPORT = re.compile(
    '^export (?P<name>[A-Za-z][A-Za-z0-9_]+)$'
)


def parse(lines: Iterable[str]) -> Tuple[OrderedDict, State]:
    # add the import (aka load) function to the namespace in advance
    namespace = OrderedDict(load=import_module)
    exports = OrderedDict()
    # strip trailing white-space characters and remove empty lines
    for line in (F(map, str.strip) >> (filter, bool))(lines):
        if DEFINITION.match(line):
            (name, expression), *_ = DEFINITION.findall(line)
            if name in namespace:
                raise RuntimeError(f'reassigning {name} in config')
            namespace[name] = _parse_expression(namespace, expression)
        elif EXPORT.match(line):
            name, *_ = EXPORT.findall(line)
            if name in exports:
                raise RuntimeError(f'multiple exports for {name} in config')
            if name not in namespace:
                raise RuntimeError(f'exporting an undefined name {name}')
            try:
                exports[name] = namespace[name]
            except KeyError:
                raise RuntimeError(f'exporting an undefined name {name!r}')
            if not isinstance(exports[name], Action):
                raise RuntimeError(f'exporting a non-action {name!r}')
        else:
            raise SyntaxError(
                f'line {line!r} is neither a valid definition, nor a valid '
                f'export'
            )
    states = [val for val in namespace.values() if isinstance(val, Stateful)]
    return exports, State(states)


def _parse_expression(namespace: Mapping, expression: str) -> Any:
    # operators == {} means that no operators can be used in the config apart
    # from compiler-specific ones (e.g. getattr and the ternary operator)
    return EvalWithCompoundTypes(
        operators={}, functions=namespace, names=namespace
    ).eval(expression)


if __name__ == '__main__':
    raise RuntimeError
