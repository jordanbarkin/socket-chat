#!/usr/bin/env python3

import socket
import threading 
import userstate

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
                data = conn.recv(4096)
            except socket.timeout:
                None

            # logic to process a message and then respond appropriately
            # call jordan's library to derserialize the message
            print(data)

            if not user:
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

            # deliver any messages in the queue 
            while not users[user].deliver_now.empty():
                message = users[user].deliver_now.get()

                # in case of failure, put the message back on the queue to avoid
                # message drops. note that the message will now be at the end of 
                # the queue, so our server does not guarantee in-order message
                # delivery.

                # i'm worried that this call might timeout too bc conn.timeout(0.5)
                # not sure if sends will also timeout?????????
                try conn.sendall(message):
                    continue
                except e:
                    users[user].deliver_now.put(message)


if __name__ == '__main__':

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((HOST, PORT))
        s.listen()
        print("server is listening")

        while True:
            conn, addr = s.accept()

            # spawn a new thread to handle each connection to allow multiple connections
            # this allows the server to maintain state for each connection 
            threading.Thread(target=thread_func, (conn,)).start()

