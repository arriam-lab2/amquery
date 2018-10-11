import asyncio
import secrets
import logging
import json
import crypt
from concurrent.futures import ThreadPoolExecutor
from hmac import compare_digest as compare_hash

from misal.core import Database
from misal.core.users import UserDatabase, User
from misal.proto import MessageType, Message, create_ssl_context, \
                        readmessage, writemessage, \
                        content_type


class Session:
    def __init__(self, user: User) -> None:
        self.user = user
        self.authenticated = False
        self.alive = True


class Server:

    def __init__(self, db: Database, user_db: UserDatabase,
                 port: int, root: str, log: logging.Logger, **kwargs):
        self._database: Database = db
        self._user_db: UserDatabase = user_db
        self._port: int = port

        # TODO create a root property in the Database class
        self._root: str = root

        self._logger: logging.Logger = log
        self._handlers = {
            MessageType.HELP: self._handle_help,
            MessageType.SYN: self._handle_syn,
            MessageType.CALL: self._handle_call,
            MessageType.STATUS: self._handle_status
        }
        # self.queue: Deque[Tuple[str, Future]] = deque()
        # setting max_workers to 1 to guarantee serial execution
        self._executor = ThreadPoolExecutor(max_workers=1)

        self._certfile = kwargs.get('certfile', None)
        self._keyfile = kwargs.get('keyfile', None)

    def _init_ssl_context(self):
        context = create_ssl_context() if self._certfile else None
        if self._certfile and self._keyfile:
            context.load_cert_chain(self._certfile, self._keyfile)
        elif self._certfile:
            context.load_cert_chain(self._certfile)
        return context

    async def run(self):
        ssl_context = self._init_ssl_context()

        if ssl_context:
            server = await asyncio.start_server(
                self.handle_client_connection,
                'localhost', self._port,
                ssl=ssl_context
            )
        else:
            server = await asyncio.start_server(
                self.handle_client_connection,
                'localhost', self._port
            )

        # TODO find a more elegant way to keep server running
        try:
            while True:
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            server.close()
            await server.wait_closed()

    async def handle_client_connection(self, reader, writer):
        session = Session(None)

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

    def _parse_message(self, message: Message):
        ctype = content_type[message.type]
        if ctype == str:
            return message.content
        else:
            return ctype(**json.loads(message.content))

    def _handle_help(self, session: Session, message: Message) -> Message:
        session.alive = False
        return Message(MessageType.RESULT, self._database.help)

    def _handle_syn(self, session: Session, message: Message) -> Message:
        content = self._parse_message(message)
        user = self._user_db.get_user(content.name)
        self._logger.info(f'Incoming authentication request '
                          f'from {content.name}')

        if user:
            crypted_pass = crypt.crypt(content.password, user.salt)
            if compare_hash(user.crypted_pass, crypted_pass):
                self._logger.info(f'{content.name} authenticated')
                session.authenticated = True
                return Message(MessageType.ACK, '')

        session.alive = False
        self._logger.info(f'Failed to authenticate {content.name}')
        return Message(MessageType.ERROR, 'Invalid username or password')

    def _handle_call(self, session: Session, message: Message) -> Message:
        # TODO keep track of calls to make status update requests possible
        callid = secrets.token_hex(8)
        self._logger.info(f'Submitting call {callid}')
        self._executor.submit(self._call, callid, message)
        session.alive = False
        return Message(MessageType.RESULT, f'Your call was submitted')

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
