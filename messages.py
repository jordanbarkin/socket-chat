from __future__ import annotations
from abc import ABC
import struct

PROTOCOL_VERSION_NUMBER = 1

# Diagnostic Message IDs
PING_MESSAGE_ID              = 0
PONG_MESSAGE_ID              = 9

# Client Message IDs
HERE_MESSAGE_ID              = 1
CREATE_ACCOUNT_MESSAGE_ID    = 2
AWAY_MESSAGE_ID              = 3
SEND_CHAT_MESSAGE_ID         = 4
REQUEST_USER_LIST_MESSAGE_ID = 5
DELETE_ACCOUNT_MESSAGE_ID    = 6
SHOW_UNDELIVERED_MESSAGE_ID  = 7

# Server Message IDs
DELIVER_MESSAGE_ID           = 10

# Packing/unpacking helpers
def pack_int(val):
    return struct.Struct("I").pack(val)

def pack_string(val):
    return pack_int(len(val)) + val

def unpack_int(buf):
    num = struct.unpack("I", buf[:4])
    return num, buf[4:]

def unpack_string(buf):
    length, rest = unpack_int(buf)
    result = rest[:length]
    return result, rest[length:]

# Base message abstract class
class Message(ABC):
    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        return cls()

    def pack_header(self) -> bytes:
        return pack_int(PROTOCOL_VERSION_NUMBER) + pack_int(self.message_type)

    def serialize(self) -> bytes:
        return pack_header()

# For diagnostic purposes
class PingMessage(Message):
    def __init__(self):
        self.message_type = PING_MESSAGE_ID

class PongMessage(Message):
    def __init__(self):
        self.message_type = PONG_MESSAGE_ID

class HereMessage(Message):
    def __init__(self, username):
        self.message_type = HERE_MESSAGE_ID
        self.username = username

    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        username, _ = unpack_string(raw)
        return cls(username)

    def serialize(self) -> bytes:
        return self.pack_header + pack_string(self.username)

class CreateAccountMessage(Message):
    def __init__(self, username):
        self.message_type = CREATE_ACCOUNT_MESSAGE_ID
        self.username = username

    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        username, _ = unpack_string(raw)
        return cls(username)

    def serialize(self) -> bytes:
        return self.pack_header() + pack_string(self.username)

class AwayMessage(Message):
    def __init__(self):
        self.message_type = AWAY_MESSAGE_ID

class SendChatMessage(Message):
    def __init__(self, username, body):
        self.message_type = SEND_CHAT_MESSAGE_ID
        self.username = username
        self.body = body

    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        username, rest = unpack_string(raw)
        body, _ = unpack_string(rest)
        return cls(username, body)

    def serialize(self) -> bytes:
        return self.pack_header() + pack_string(self.username) + pack_string(self.body)

class RequestUserListMessage(Message):
    def __init__(self):
        self.message_type = REQUEST_USER_LIST_MESSAGE_ID

class DeleteAccountMessage(Message):
    def __init__(self):
        self.message_type = DELETE_ACCOUNT_MESSAGE_ID

class ShowUndeliveredMessage(Message):
    def __init__(self):
        self.message_type = SHOW_UNDELIVERED_MESSAGE_ID

class DeliverMessage(Message):
    def __init__(self, message_list : tuple[str, str]):
        self.message_type = DELIVER_MESSAGE_ID
        self.message_list = message_list

    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        num_messages, rest = unpack_int(raw)

        messages = []

        for i in range(num_messages):
            sender, rest = unpack_string(rest)
            body, rest = unpack_string(rest)
            messages += (sender, body)

        return cls(messages)

    def serialize(self) -> bytes:
        result = self.pack_header() + pack_int(len(self.message_list))

        for sender, body in message_list
            result += pack_string(sender)
            result += pack_string(body)

        return result

# All instantiatable message types
message_classes = [
    PingMessage,
    HereMessage,
    CreateAccountMessage,
    AwayMessage,
    SendChatMessage,
    RequestUserListMessage,
    DeleteAccountMessage,
    ShowUndeliveredMessage,
    PongMessage,
    ShowUndeliveredMessageResponse,
    PollResponse
]

# Map message classes to their identifiers
id_to_class_table = { cls.message_type, cls for cls in message_classes }

def deserialize_message(raw_bytes) -> Message:

    # version number must be present
    try:
        version_num, raw_bytes = unpack_int(raw_bytes)
    except:
        raise Exception("Deserialize message failed: no version number present.")

    # version number must be correct
    if version_num != PROTOCOL_VERSION_NUMBER:
        raise Exception("Deserialize message failed: different protocol version numbers")

    # message id must be present
    try:
        message_id, raw_bytes = unpack_int(raw_bytes)
    except:
        raise Exception("Deserialize message failed: no message id present.")

    # message id must have a class
    try:
        TargetClass = id_to_class_table[message_id]
    except:
        raise Exception("Deserialize message failed: invalid message type.")

    # deserialize with correct class
    return TargetClass.deserialize(raw_bytes)


