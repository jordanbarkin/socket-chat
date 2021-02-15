#!/usr/bin/env python3

import socket
import threading
from userstate import *
from messages import *

HOST = 'localhost'
PORT = 12345

# dictionary mapping usernames:UserStates for all users in the system
# users are added when accounts are created and removed upon account deletion
# note that the server has no persistent storage. this was a design decision
# to reduce developer time. if this server needed to be more robust or reliable,
# we would add persistent state.
users = {}

# helper functions

# send all new messages to a user over the connection by emptying the user's
# deliver queue
def send_new_messages(user, conn):
    messages = []

    while user and not users[user].deliver_now.empty():
        messages.append(users[user].deliver_now.get())

    if messages:
        conn.sendall(DeliverMessage(messages).serialize())

# Read a complete message into a buffer, and deserialize it into its appropriate
# subclass of message.
def read_message(conn):
    # exception will be raised if no data is available before the timeout
    try:
        raw_message = conn.recv(4096)
    except socket.timeout:
        return None

    # message length does not include headers
    message_len = extract_length(raw_message) + 12
    current_len = len(raw_message)

    # loop until we recieve the whole message
    # ToDo add a timeout here too
    while current_len < message_len:
        data = conn.recv(4096)
        current_len += len(data)
        raw_message += data

    try:
        result = deserialize_message(raw_message)
    except Exception as e:
        print("Failed to deserialize message " + str(e.message))
        return None

    return result

# package and send <err_msg> to the client on conn
def send_error_message(conn, err_msg):
    response = ErrorMessage(err_msg)
    conn.send(response.serialize())

# handle a single request from the client.
def handle_request(user, conn, message):

    # Predicate for whether a message requires you to be logged in to
    # use it.
    def message_requires_logged_in(message_type):
        return message_type not in [CreateAccountMessage, HereMessage]

    message_type = type(message)
    print("Received a " + str(message_type))

    # Next, we process the message, conditioning on type.

    # Ping case
    if message_type == PingMessage:
        conn.send(PongMessage().serialize())

    # users need to be "here" to use most features
    elif not user and message_requires_logged_in(message_type):
        send_error_message(conn, "Please log in or create an account before making requests.")

    # similar to a login method, except that our server does not authenticate users :O
    elif message_type == HereMessage:
        try:
            # users[message.username]
            user = message.username
            users[user].login()
        except:
            send_error_message(conn, "Account does not exist.")

    # the user is also automatically marked as "here" for the newly created account
    elif message_type == CreateAccountMessage:
        user = message.username
        users.update({user: UserState(user)})
        users[user].login()

        # add to permanent acccount list
        with (open("users.txt", "a+")) as f:
            f.write(user + "\n")

    # again, like a logout without authentication
    elif message_type == AwayMessage:
        if user in users:
            users[user].logout()
            user = None
        else:
            send_error_message(conn, "Account does not exist")

    # will be delivered immediately or on demand depending on target's "here" status
    # note that add_message handles that logic
    elif message_type == SendChatMessage:
        target = message.username.strip()

        if target not in users:
            send_error_message(conn, "Recipient user does not exist. Please try again.")
        else:
            print("Received email for ", target)
            users[target].add_message((user, message.body))

    # send back a list of all users
    elif message_type == RequestUserListMessage:
        response = UserListResponseMessage(list(users.keys()))
        conn.send(response.serialize())

    # you can only delete yourself for security reasons
    elif message_type == DeleteAccountMessage:
        if not user:
            send_error_message(conn, "Please log in to delete your account.")
        else:
            users.pop(user)
            user = None

    # note that we deliver undelivered messages recieved both while the user was
    # "away" and "here"
    elif message_type == ShowUndeliveredMessage:
        messages = []

        while not users[user].deliver_later.empty():
            messages.append(users[user].deliver_later.get())

        while not users[user].deliver_now.empty():
            messages.append(users[user].deliver_now.get())

        response = DeliverMessage(messages)
        conn.send(response.serialize())

    else:
        print("Unable to handle request. Invalid message type")

    return user

# A per-user thread runs this loop to handle requests and dispatch new
# server to client messages.
def connection_thread(conn):
    user = None

    # set a timeout of 0.5 seconds to avoid blocking on the socket
    conn.settimeout(0.5)
    with conn:
        while True:
            # deliver any messages in the user's queue
            send_new_messages(user, conn)

            # process any new request from the client
            request = read_message(conn)

            if request:
                try:
                    user = handle_request(user, conn, request)
                except:
                    print("Failed to handle request for an unknown reason.")

# Read the list of users from the user log and resume the server state
# with those users.
# Note that messsages, unlike user acccounts, do not persist across server
# restarts.
def load_users(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            username = line.strip()
            users.update({username: UserState(username)})


if __name__ == '__main__':
    # resume with users if file exists
    try:
        load_users("users.txt")
    except:
        pass

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server listening on", HOST, ":", PORT)

        while True:
            conn, addr = s.accept()

            # spawn a new thread to handle each new connection to allow multiple simultaneous connections
            # this allows the server to maintain state for each connection
            threading.Thread(target=connection_thread, args=(conn,)).start()

