import asyncio
import json
import secrets
import logging
from concurrent.futures import ThreadPoolExecutor
# from collections import deque
from enum import Enum, auto
from typing import NamedTuple, Any

from misal.core import Database

MSGTYPE = 'TYPE'
MSGCONTENT = 'CONTENT'
MSGKEY = 'KEY'


class MessageType(Enum):
    HELP = auto()
    CALL = auto()
    RESULT = auto()
    STATUS = auto()
    ERROR = auto()


Message = NamedTuple('Message', [
    ('type', MessageType), ('key', str), ('content', Any)
])


class Server:

    def __init__(self, db: Database, port: int, key: str, log: logging.Logger):
        self._database = db
        self._port = port
        self._key = key
        self._logger = log
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
        # receive a message
        message = await readmessage(reader)
        # TODO we can provide docs without authentication
        if message.key != self._key:
            self._logger.info('Failed to authenticate a client')
            response = Message(
                MessageType.ERROR, '', 'Invalid authentication key'
            )
        elif message.type is MessageType.HELP:
            response = Message(
                MessageType.RESULT, '', self._database.help
            )
        elif message.type is MessageType.CALL:
            # submit the call
            # TODO keep track of calls to make status update requests possible
            callid = secrets.token_hex(8)
            self._logger.info(f'Submitting call {callid}')
            self._executor.submit(self._call, callid, message)
            response = Message(
                MessageType.RESULT, '',
                f'Your call was submitted'
            )
        elif message.type is MessageType.STATUS:
            response = Message(
                MessageType.ERROR, '',
                f'Status checks are not implemented yet'
            )
        else:
            self._logger.info(f'Received a message of unknown type {message.type}')
            response = Message(
                MessageType.ERROR, '', 'Unrecognised message type'
            )
        writemessage(writer, response)

    def _call(self, callid: int, message: Message):
        try:
            action_name, *args = message.content
            retval = self._database.call(action_name, *args)
            self._logger.info(f'Finished processing call {callid}')
            return retval
        except Exception as err:
            self._logger.exception(str(err))


async def readmessage(reader: asyncio.StreamReader) -> Message:
    message = await reader.readline()
    decoded = json.loads(message.decode())
    return Message(MessageType(decoded[MSGTYPE]), decoded[MSGKEY], decoded[MSGCONTENT])


def writemessage(writer: asyncio.StreamWriter, message: Message):
    jsonised = json.dumps({
        MSGTYPE: message.type.value,
        MSGKEY: message.key,
        MSGCONTENT: message.content
    })
    encoded = (jsonised + '\n').encode()
    writer.write(encoded)
    writer.drain()


async def client_connection(port: int, message: Message):
    reader, writer = await asyncio.open_connection('localhost', port)
    writemessage(writer, message)
    response = await readmessage(reader)
    print(response.content)
    asyncio.get_event_loop().stop()


if __name__ == '__main__':
    raise RuntimeError
