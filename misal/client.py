import asyncio
import crypt
from misal.protocol import Message, MessageType, writemessage, readmessage


class Session:
    def __init__(self, address: str, port: int,
                 user: str, password: str) -> None:
        self._address: str = address
        self._port: int = port
        self._user: str = user
        self._password: str = password
        self._token: str = None

    @property
    def address(self) -> str:
        return self._address

    @property
    def port(self) -> int:
        return self._port

    @property
    def user(self) -> str:
        return self._user

    @property
    def password(self) -> str:
        return self._password

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, value) -> None:
        self._token = value


class Client:
    def __init__(self, address: str, port: int, user: str,
                 password: str, query: str):
        self._query = query
        self._session = Session(address, port, user, password)
        self._keep_alive = True
        self._handlers = {
            MessageType.AUTH: self._handle_auth,
            MessageType.ESTABLISHED: self._handle_established,
            MessageType.RESULT: self._handle_result,
            MessageType.ERROR: self._handle_error
        }

    @property
    def session(self) -> Session:
        return self._session

    async def run(self) -> None:
        if self._query:
            first_message = Message(MessageType.SYN, '', self.session.user)
        else:
            first_message = Message(MessageType.HELP, '', '')

        await self.connect(first_message)

    async def connect(self, message: Message):
        try:
            reader, writer = await asyncio.open_connection(
                self.session.address,
                self.session.port
            )

            while self._keep_alive:
                writemessage(writer, message)
                response = await readmessage(reader)
                message = self._handlers[response.type](response)
                if not message:
                    self._keep_alive = False

        except Exception as error:
            print(str(error))
        finally:
            asyncio.get_event_loop().stop()

    def _handle_auth(self, response: Message) -> Message:
        self.session.token = response.key
        return Message(
            MessageType.AUTH,
            self.session.token,
            crypt.crypt(self.session.password, salt=response.content)
        )

    def _handle_established(self, response: Message) -> Message:
        return Message(
            MessageType.CALL,
            self.session.token,
            self._query
        )

    def _handle_result(self, response: Message) -> None:
        print(response.content)

    def _handle_error(self, response: Message) -> None:
        print(response.content)
