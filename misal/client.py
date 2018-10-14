import asyncio
import ssl
import json
from typing import NamedTuple
from misal.proto import Message, MessageType, \
                        writemessage, readmessage, \
                        content_type


UserCredentials = NamedTuple('UserCredentials', [
    ('name', str), ('password', str)
])


class Session:
    def __init__(self, address: str, port: int) -> None:
        self.address: str = address
        self.port: int = port


class Client:
    def __init__(self, address: str, port: int, user: str,
                 password: str, query: str, **kwargs):
        self._query = query
        self._session = Session(address, port)
        self._user_creds = UserCredentials(user, password)
        self._keep_alive = True
        self._handlers = {
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
                message = self._make_message(
                    MessageType.SYN,
                    name=self._user_creds.name,
                    password=self._user_creds.password)
            else:
                message = self._make_message(MessageType.HELP, content='')

            while self._keep_alive:
                writemessage(writer, message)
                response = await readmessage(reader)
                message = self._handlers[response.type](response)
                if not message:
                    self._keep_alive = False

        except Exception as error:
            print(error)
            raise
        finally:
            writer.close()
            asyncio.get_event_loop().stop()

    def _make_message(self, message_type: MessageType, **kwargs) -> Message:
        ctype = content_type[message_type]
        if ctype != str:
            content = ctype(*kwargs.values())._asdict()
            return Message(message_type, json.dumps(content))
        else:
            return Message(message_type, kwargs.get('content', ''))

    def _handle_auth(self, response: Message) -> Message:
        return self._make_message(MessageType.AUTH, content='')

    def _handle_ack(self, response: Message) -> Message:
        return self._make_message(MessageType.CALL, content=self._query)

    def _handle_result(self, response: Message) -> None:
        print(response.content)

    def _handle_error(self, response: Message) -> None:
        print(response.content)
