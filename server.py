#!/usr/bin/env python3

import socket
import threading 
import userstate
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
            
            # exception will be raised if no data is available before the timout
            try:
                message = conn.recv(4096)
            except socket.timeout:
                None
           
            message_len = int.from_bytes(raw_message[8:13])

            # message length does not include header length
            current_len = len(raw_message - 12)
            
            # loop until we recieve the whole message
            while current_len < message_len:
                data = conn.recv(4096)
                current_len += len(data)
                raw_message += data
            
            message = messages.deserialize_message(raw_message)
            message_type = type(message)
            # logic to process a message and then respond appropriately
            # call jordan's library to derserialize the message
            
            if (message_type == PingMessage):
                response = PongMessage()
                conn.send(response.serialize())
            else if not user and (message_type not in [CreateAccountMessage, AwayMessage, HereMessage]):
                response = ErrorMessage()
                conn.send(response.seralize())
            else if message_type == HereMessage:
                user = message.username
            else if message_type == CreateAccountMessage:
                user = message.username
                users.update({user: })
              # should have message type here or create account 
                print("TODO")
              # set user to username 
            else:
                # switch on message type and process appropriately
                # create account
                # here 
                # away
                # email send -> bulk of work
                # ping 
                # list clients 
                # delete account 
                # show undelivered messages
                print("hi")

            # deliver any messages in the queue 
            while not users[user].deliver_now.empty():
                message = users[user].deliver_now.get()

                # in case of failure, put the message back on the queue to avoid
                # message drops. note that the message will now be at the end of 
                # the queue, so our server does not guarantee in-order message
                # delivery.

                # i'm worried that this call might timeout too bc conn.timeout(0.5)
                # not sure if sends will also timeout?????????
                try:
                    conn.sendall(message)
                except e:
                    users[user].deliver_now.put(message)


if __name__ == '__main__':
    print(type(3))
    print(type(3) == int)

def ugh():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((HOST, PORT))
        s.listen()
        print("server is listening")

        while True:
            conn, addr = s.accept()

            # spawn a new thread to handle each connection to allow multiple connections
            # this allows the server to maintain state for each connection 
            threading.Thread(target=thread_func, args=(conn,)).start()

