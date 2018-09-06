import asyncio
import json
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
    ERROR = auto()


Message = NamedTuple('Message', [
    ('type', MessageType), ('key', str), ('content', Any)
])


class Server:

    def __init__(self, database: Database, port: int, key: str):
        self.database = database
        self.port = port
        self.key = key
        self.queue = []

    async def run(self):
        server = await asyncio.start_server(
            self.communicate, 'localhost', self.port
        )
        # TODO find a more elegant way to keep server running
        try:
            while True:
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            server.close()
            await server.wait_closed()

    async def communicate(self, reader, writer):
        # receive a message
        message = await readmessage(reader)

        if message.key != self.key:
            response = Message(
                MessageType.ERROR, '', 'Invalid authentication key'
            )
        elif message.type is MessageType.HELP:
            response = Message(
                MessageType.RESULT, '', self.database.help
            )
        elif message.type is MessageType.CALL:
            self.queue.append(message.content)
            response = Message(
                MessageType.RESULT, '',
                f'Your call is number {len(self.queue)} in line'
            )
        else:
            response = Message(
                MessageType.ERROR, '', 'Unrecognised message type'
            )
        writemessage(writer, response)


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


async def client(port: int, message: Message):
    reader, writer = await asyncio.open_connection('localhost', port)
    writemessage(writer, message)
    response = await readmessage(reader)
    print(response.content)
    asyncio.get_event_loop().stop()


if __name__ == '__main__':
    raise RuntimeError
