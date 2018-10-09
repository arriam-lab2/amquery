import asyncio
import ssl
from typing import NamedTuple
from misal.proto import Message, MessageType, \
                        writemessage, readmessage


UserCredentials = NamedTuple('UserCredentials', [
    ('user', str), ('password', str)
])


class Session:
    def __init__(self, address: str, port: int,
                 token: str) -> None:
        self.address: str = address
        self.port: int = port
        self.token: str = token


class Client:
    def __init__(self, address: str, port: int, user: str,
                 password: str, query: str, **kwargs):
        self._query = query
        self._session = Session(address, port, None)
        self._user_creds = UserCredentials(user, password)
        self._keep_alive = True
        self._handlers = {
            MessageType.AUTH: self._handle_auth,
            MessageType.ACK: self._handle_ack,
            MessageType.RESULT: self._handle_result,
            MessageType.ERROR: self._handle_error
        }
        self._certfile = kwargs.get('certfile', None)

    async def _open_connection(self):
        if self._certfile:
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                                     cafile=self._certfile)
            return await asyncio.open_connection(
                self._session.address, self._session.port,
                ssl=ssl_context
            )
        else:
            return await asyncio.open_connection(
                self._session.address, self._session.port
            )

    async def run(self) -> None:
        try:
            reader, writer = await self._open_connection()

            if self._query:
                message = Message(
                    MessageType.SYN,
                    "HELLO",
                )
            else:
                message = Message(MessageType.HELP, '')

            while self._keep_alive:
                writemessage(writer, message)
                response = await readmessage(reader)
                message = self._handlers[response.type](response)
                if not message:
                    self._keep_alive = False

        except Exception as error:
            print(error)
        finally:
            writer.close()
            asyncio.get_event_loop().stop()

    def _handle_auth(self, response: Message) -> Message:
        return Message(MessageType.AUTH, '')

    def _handle_ack(self, response: Message) -> Message:
        return Message(MessageType.CALL, '')

    def _handle_result(self, response: Message) -> None:
        print(response.content)

    def _handle_error(self, response: Message) -> None:
        print(response.content)
