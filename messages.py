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
USER_LIST_RESPONSE_ID        = 11
ERROR_MESSAGE_ID             = 12

# Packing/unpacking helpers

# Pack an int into a byte array.
def pack_int(val):
    return struct.Struct("I").pack(val)

# Pack a string with its length into a byte array.
def pack_string(val):
    return pack_int(len(val)) + str.encode(val)

# Unpack a 4 byte integer off of the front of a byte array.
# Returns the integer and the rest of the message.
def unpack_int(buf):
    num = struct.unpack("I", buf[:4])
    return num[0], buf[4:]

# Unpack a string in our encoding off the front of a byte array.
# Returns the string and the rest of the message.
# Note that this involves grabbing the 4 byte size from the front,
# and then extracting the string of that length.
def unpack_string(buf):
    length, rest = unpack_int(buf)
    result = rest[:length]
    return result.decode(), rest[length:]

# Extracts the length of a message, given at *least* its first 12 bytes.
def extract_length(buf):
    return struct.unpack("I", buf[8:12])[0]

# Base message abstract class
class Message(ABC):
    # Every Message subclass must provide a way to deserialize itself from
    # bytes sent over the network.
    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        return cls()

    # Every message starts with the same 8 byte header, containing
    def pack_header(self) -> bytes:
        return pack_int(PROTOCOL_VERSION_NUMBER) + pack_int(self.message_type)

    # Every Message subclass must provide a way to serialize its payload,
    # that is, everything after the first 12 bytes (header and length.
    # In many messages that just send integer flags, the payload is empty and
    # inherited from here.
    def serialize_payload(self) -> int:
        return b'' # no payload

    # To serialize a message, we serialize its payload (which varies by message type)
    # and then pack it with the standard header and its length.
    # This is called on any message to return the bytes that should be sent
    # over the wire.
    def serialize(self) -> bytes:
        payload = self.serialize_payload()
        return self.pack_header() + pack_int(len(payload)) + payload

# Represents an empty message that should be responded to with a PongMessage.
class PingMessage(Message):
    message_type = PING_MESSAGE_ID

# Response to a PingMessage
class PongMessage(Message):
    message_type = PONG_MESSAGE_ID

# The following are essages that the client can send to the server.

# Indicates that <username> wants to log in.
class HereMessage(Message):
    message_type = HERE_MESSAGE_ID

    def __init__(self, username):
        self.username = username

    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        username, _ = unpack_string(raw)
        return cls(username)

    def serialize_payload(self) -> bytes:
        return pack_string(self.username)

# Indicates that a user wants to create an account with name <username>.
class CreateAccountMessage(Message):
    message_type = CREATE_ACCOUNT_MESSAGE_ID

    def __init__(self, username):
        self.username = username

    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        username, _ = unpack_string(raw)
        return cls(username)

    def serialize_payload(self) -> bytes:
        return pack_string(self.username)

# Logs a user out.
class AwayMessage(Message):
    message_type = AWAY_MESSAGE_ID

# Send a chat to <username> with message <body>
class SendChatMessage(Message):
    message_type = SEND_CHAT_MESSAGE_ID

    def __init__(self, username, body):
        self.username = username
        self.body = body

    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        username, rest = unpack_string(raw)
        body, _ = unpack_string(rest)
        return cls(username, body)

    def serialize_payload(self) -> bytes:
        return pack_string(self.username) + pack_string(self.body)

# Server will reply with a UserListResponseMessage
class RequestUserListMessage(Message):
    message_type = REQUEST_USER_LIST_MESSAGE_ID

# User wants to delete their account.
class DeleteAccountMessage(Message):
    message_type = DELETE_ACCOUNT_MESSAGE_ID

# Server will reply with a DeliverMessage
class ShowUndeliveredMessage(Message):
    message_type = SHOW_UNDELIVERED_MESSAGE_ID

# Either a response to ShowUndeliveredMessage, or dispatched whenever
# a message is sent to a currently logged in user.
class DeliverMessage(Message):
    message_type = DELIVER_MESSAGE_ID

    def __init__(self, message_list : list[tuple[str, str]]):
        self.message_list = message_list

    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        num_messages, rest = unpack_int(raw)

        messages = []

        for i in range(num_messages):
            sender, rest = unpack_string(rest)
            body, rest = unpack_string(rest)
            messages.append((sender, body))

        return cls(messages)

    def serialize_payload(self) -> bytes:
        result = pack_int(len(self.message_list))

        for sender, body in self.message_list:
            result += pack_string(sender)
            result += pack_string(body)

        return result

# Reply to RequestUserListMessage
# Contains a list of all users.
class UserListResponseMessage(Message):
    message_type = USER_LIST_RESPONSE_ID

    def __init__(self, user_list : list[str]):
        self.user_list = user_list

    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        num_users, rest = unpack_int(raw)

        users = []

        for i in range(num_users):
            user, rest = unpack_string(rest)
            users.append(user)

        return cls(users)

    def serialize_payload(self) -> bytes:
        result = pack_int(len(self.user_list))

        for user in self.user_list:
            result += pack_string(user)

        return result

# Wraps an error message string to be sent to the client.
class ErrorMessage(Message):
    message_type = ERROR_MESSAGE_ID

    def __init__(self, error_message):
        self.error_message = error_message

    @classmethod
    def deserialize(cls, raw : bytes) -> Message:
        error_message, _ = unpack_string(raw)
        return cls(error_message)

    def serialize_payload(self) -> bytes:
        return pack_string(self.error_message)

# All instantiatable message types
message_classes = [
    PingMessage,
    PongMessage,
    HereMessage,
    CreateAccountMessage,
    AwayMessage,
    SendChatMessage,
    RequestUserListMessage,
    DeleteAccountMessage,
    ShowUndeliveredMessage,
    DeliverMessage,
    UserListResponseMessage,
    ErrorMessage
]

# Map message types to their classes
id_to_class_table = { c.message_type: c for c in message_classes }

# Given the bytes of a full message, extract the message type and dispatch
# the payload to the correct class's deserialize function.
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

    try:
        payload_size, payload = unpack_int(raw_bytes)
    except:
        raise Exception("Payload size not present")

    # message id must have a class
    try:
        TargetClass = id_to_class_table[message_id]
    except:
        raise Exception("Deserialize message failed: invalid message type.")

    try:
        return TargetClass.deserialize(payload)
    except:
        raise Exception("Message payload does not match message type.")



