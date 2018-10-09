import asyncio
import json
import ssl
from enum import Enum, auto
from typing import NamedTuple, Any


MSGTYPE = 'TYPE'
MSGCONTENT = 'CONTENT'
MSGKEY = 'KEY'


class MessageType(Enum):
    HELP = auto()
    SYN = auto()
    AUTH = auto()
    ACK = auto()
    CALL = auto()
    RESULT = auto()
    STATUS = auto()
    ERROR = auto()
    FIN = auto()


Message = NamedTuple('Message', [
    ('type', MessageType), ('content', Any)
])

AuthMessageContent = NamedTuple('AuthMessageContent', [
    ('user', str), ('password', str)
])


def create_ssl_context(proto=ssl.PROTOCOL_SSLv23, verify_mode=ssl.CERT_NONE,
                       protocols=None, options=None, ciphers="ALL"):
    protocols = protocols or ('PROTOCOL_TLS')
    options = options or ('OP_CIPHER_SERVER_PREFERENCE', 'OP_SINGLE_DH_USE',
                          'OP_SINGLE_ECDH_USE', 'OP_NO_COMPRESSION')
    context = ssl.SSLContext(proto)
    context.verify_mode = verify_mode
    
    # reset protocol and options
    context.protocol = 0
    context.options = 0
    for p in protocols:
        context.protocol |= getattr(ssl, p, 0)
    for o in options:
        context.options |= getattr(ssl, o, 0)
    context.set_ciphers(ciphers)
    return context


async def readmessage(reader: asyncio.StreamReader) -> Message:
    message = await reader.readline()
    decoded = json.loads(message.decode())
    return Message(MessageType(decoded[MSGTYPE]), decoded[MSGCONTENT])


def writemessage(writer: asyncio.StreamWriter, message: Message):
    jsonised = json.dumps({
        MSGTYPE: message.type.value,
        MSGCONTENT: message.content
    })
    encoded = (jsonised + '\n').encode()
    writer.write(encoded)
    writer.drain()
