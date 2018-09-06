from typing import Iterable, Mapping, List, Tuple

from misal.core import Action, State


__all__ = ['Database']


def format_help(action: Action) -> str:
    description = action.description
    argdocs = '\n'.join(
        f'\t{name}: {doc or "..."}' for name, doc in action.arguments
    )
    return f'''\
    ACTION:
    \t{action}
    DESCRIPTION:
    \t{description}
    ARGUMENTS:
    {argdocs}
    '''


class Database:

    def __init__(self, name: str, state: State, actions: Iterable[Action]):
        # TODO should we run on something else but localhost?
        self._name = name
        self._state = state
        self._actions: Mapping[str, Action] = {
            action.name: action for action in actions
        }

    @property
    def help(self) -> str:
        actions = map(format_help, self._actions.values())
        return '\n'.join([f'Misal database {self.name}', *actions])

    @property
    def name(self) -> str:
        return self._name

    def call(self, name: str, *args):
        action = self._actions.get(name)
        if action is None:
            raise RuntimeError(
                f'Action {name} is not available in {type(self).__name__} '
                f'{self.name}'
            )
        with self._state(action.save):
            feedback = action(*args)
            return feedback


if __name__ == '__main__':
    raise RuntimeError
