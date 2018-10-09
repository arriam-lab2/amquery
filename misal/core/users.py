import getpass
import crypt
import pathlib
import secrets
from enum import Enum
from typing import NamedTuple
from pony.orm import Database, Required, db_session, select


class UserPrivelege(str, Enum):
    ADMIN: str = "ADMIN"
    READ_ONLY: str = "RO"
    READ_WRITE: str = "RW"


db = Database()


UserData = NamedTuple('UserData', [
    ('name', str), ('crypted_pass', str),
    ('salt', str), ('privelege', UserPrivelege)
])


class User(db.Entity):
    name = Required(str)
    crypted_pass = Required(str)
    salt = Required(str)
    privelege = Required(UserPrivelege)


class UserDatabase:

    def __init__(self, name: str) -> None:
        self._name = name if name else secrets.token_hex(8)

        pathlib.Path(self.root).mkdir(parents=True, exist_ok=True)
        db.bind(provider='sqlite', filename=self.file, create_db=True)
        db.generate_mapping(check_tables=True, create_tables=True)

        self._init()

    @property
    def name(self) -> str:
        return self._name

    @property
    def file(self) -> str:
        return f'{self.root}/users.sqlite'

    @property
    def root(self) -> str:
        home = str(pathlib.Path.home())
        return f'{home}/.misal/{self.name}'

    @db_session
    def _init(self) -> None:
        if not User.select().exists():
            self.add_user(privelege=UserPrivelege.ADMIN)

    @db_session
    def add_user(self, **kwargs) -> None:
        name = kwargs.get('name', None)
        name = name if name else _input_name()
        salt = kwargs.get('salt', None)
        crypted_pass = kwargs.get('crypted_pass', None)
        if not crypted_pass:
            password = _input_password()
            salt = make_salt()
            crypted_pass = crypt.crypt(password, salt=salt)

        privelege = kwargs.get('privelege', None)
        privelege = privelege if privelege else _input_privelege()

        User(name=name, crypted_pass=crypted_pass,
             salt=salt, privelege=privelege)

    @db_session
    def get_user(self, name) -> User:
        users = select(u for u in User if u.name == name)
        return users.first() if users.count() else None


def make_salt() -> str:
    return crypt.mksalt()


def _input_name() -> str:
    return input("Enter username: ")


def _input_password() -> str:
    password = getpass.getpass('Enter password:')
    new_password = getpass.getpass('Retype password:')
    if password != new_password:
        raise RuntimeError("Sorry, passwords do not match.")
    return new_password


def _input_privelege() -> UserPrivelege:
    return UserPrivelege.READ_ONLY


def authentificate(**kwargs) -> str:
    name = kwargs.get('name', None)
    if not name:
        name = input("Username:")

    password = kwargs.get('password', None)
    if not password:
        password = getpass.getpass('Password:')


if __name__ == '__main__':
    raise RuntimeError
