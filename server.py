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

def thread_func(conn):

    user = None

    # set a timeout of 0.5 seconds to avoid blocking on the socket
    conn.settimeout(0.5)
    with conn:
        while True:
            
            # deliver any messages in the queue 
            messages = []
            while user and not users[user].deliver_now.empty():
                messages.append(users[user].deliver_now.get())
            
            if len(messages) != 0:
                conn.sendall(DeliverMessage(messages).serialize())

            # exception will be raised if no data is available before the timeout
            try:
                raw_message = conn.recv(4096)
                print(raw_message)
            except socket.timeout:
                continue
           
            # message length does not include headers
            message_len = extract_length(raw_message)
            current_len = len(raw_message)
            
            # loop until we recieve the whole message
            while current_len < message_len:
                data = conn.recv(4096)
                current_len += len(data)
                raw_message += data
            
            message = deserialize_message(raw_message)
            message_type = type(message)
           
            # process message, switching on type
            if message_type == PingMessage:
                response = PongMessage()
                conn.send(response.serialize())
            # users need to be "here" to use most features
            elif not user and (message_type not in [CreateAccountMessage, HereMessage]):
                response = ErrorMessage("must be logged in to do that")
                conn.send(response.serialize())
            # similar to a login method, except that our server does not authenticate users :O
            elif message_type == HereMessage:
                user = message.username
            # the user is also automatically marked as "here" for the newly created account
            elif message_type == CreateAccountMessage:
                user = message.username
                users.update({user: UserState(user)})
            # again, like a logout without authentication
            elif message_type == AwayMessage:
                user = None
                users[user].here = False
            # will be delivered immediately or on demand depending on target's "here" status
            # note that add_message handles that logic
            elif message_type == SendChatMessage:
                target = message.username
                users[target].add_message((target, message.body))
            elif message_type == RequestUserListMessage:
                response = UserListResponseMessage(users.keys())
                conn.send(response.serialize())
            # you can only delete yourself for security reasons
            elif message_type == DeleteAccountMessage:
                if not user: 
                    conn.send(ErrorMessage("must be here to delete account").serialize())
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
                conn.send(response.serialize)


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((HOST, PORT))
        s.listen()
        print("server is listening")

        while True:
            conn, addr = s.accept()

            # spawn a new thread to handle each connection to allow multiple connections
            # this allows the server to maintain state for each connection 
            threading.Thread(target=thread_func, args=(conn,)).start()

