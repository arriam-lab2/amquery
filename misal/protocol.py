import asyncio
import json
from enum import Enum, auto
from typing import NamedTuple, Any


MSGTYPE = 'TYPE'
MSGCONTENT = 'CONTENT'
MSGKEY = 'KEY'


class MessageType(Enum):
    HELP = auto()
    SYN = auto()
    AUTH = auto()
    ESTABLISHED = auto()
    CALL = auto()
    RESULT = auto()
    STATUS = auto()
    ERROR = auto()
    FIN = auto()


Message = NamedTuple('Message', [
    ('type', MessageType), ('key', str), ('content', Any)
])


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
