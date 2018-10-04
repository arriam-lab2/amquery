import asyncio
import secrets
import logging
from concurrent.futures import ThreadPoolExecutor
# from collections import deque
from hmac import compare_digest as compare_hash

from misal.core import Database
from misal.core.users import UserDatabase, User, make_salt
from misal.protocol import MessageType, Message, \
                           readmessage, writemessage


class Session:
    def __init__(self, token: str, user: User) -> None:
        self.token = token
        self.user = user
        self.authentificated = False
        self.alive = True


class Server:

    def __init__(self, db: Database, user_db: UserDatabase,
                 port: int, root: str,
                 log: logging.Logger):
        self._database: Database = db
        self._user_db: UserDatabase = user_db
        self._port: int = port

        # TODO create a root property in the Database class
        self._root: str = root
        
        self._logger: logging.Logger = log
        self._handlers = {
            MessageType.HELP: self._handle_help,
            MessageType.SYN: self._handle_syn,
            MessageType.AUTH: self._handle_auth,
            MessageType.CALL: self._handle_call,
            MessageType.STATUS: self._handle_status
        }
        # self.queue: Deque[Tuple[str, Future]] = deque()
        # setting max_workers to 1 to guarantee serial execution
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def run(self):
        server = await asyncio.start_server(
            self.handle_client_connection, 'localhost', self._port
        )
        # TODO find a more elegant way to keep server running
        try:
            while True:
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            server.close()
            await server.wait_closed()

    async def handle_client_connection(self, reader, writer):
        token = secrets.token_hex(8)
        session = Session(token, None)

        # TODO add a timeout parameter
        while session.alive:
            message = await readmessage(reader)

            if message.type in self._handlers:
                response = self._handlers[message.type](session, message)
            else:
                self._logger.info(f'Received a message of unknown '
                                  'type {message.type}')
                session.alive = False
                response = Message(
                    MessageType.ERROR, '', 'Unrecognised message type'
                )

            writemessage(writer, response)

    def _handle_help(self, session: Session, message: Message) -> Message:
        session.alive = False
        return Message(MessageType.RESULT, '', self._database.help)

    def _handle_syn(self, session: Session, message: Message) -> Message:
        username = message.content
        self._logger.info(f'Authentification request from {username}')

        user = self._user_db.get_user(username)
        if user:
            session.user = user
            salt = user.salt if user else make_salt()
            return Message(MessageType.AUTH, session.token, salt)
        else:
            session.alive = False
            return Message(
                MessageType.ERROR, '', 'Invalid username or password'
            )

    def _handle_auth(self, session: Session, message: Message) -> Message:
        crypted_pass = message.content
        if compare_hash(session.user.crypted_pass, crypted_pass):
            self._logger.info(f'{session.user.name} authentificated')
            session.authenticated = True
            response = Message(MessageType.ESTABLISHED, '', '')
        else:
            self._logger.info(f'Failed to authentificate {session.user.name}')
            response = Message(
                MessageType.ERROR, '', 'Invalid username or password'
            )
            session.alive = False
        return response

    def _handle_call(self, session: Session, message: Message) -> Message:
        # TODO keep track of calls to make status update requests possible
        callid = secrets.token_hex(8)
        self._logger.info(f'Submitting call {callid}')
        self._executor.submit(self._call, callid, message)
        session.alive = False
        return Message(MessageType.RESULT, '', f'Your call was submitted')

    def _call(self, callid: int, message: Message):
        try:
            action_name, *args = message.content
            retval = self._database.call(action_name, *args)
            self._logger.info(f'Finished processing call {callid}')
            return retval
        except Exception as err:
            # TODO update a call status instead
            self._logger.exception(str(err))

    def _handle_status(self, session: Session, message: Message) -> Message:
        session.alive = False
        return Message(MessageType.ERROR, '',
                       f'Status checks are not implemented yet'
                       )


if __name__ == '__main__':
    raise RuntimeError
