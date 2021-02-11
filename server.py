#!/usr/bin/env python3

import socket
from _thread import *
import threading 
import userstate

HOST = 'localhost'
PORT = 12345
users = {}

def thread_func(conn):

    user = None
    with conn:
        while True:
            
            # This call will block if the connection is open but no data is being
            # sent. In order to avoid message delivery delays, the client will 
            # constantly ping the server, effectively converting to a polling model.
            # This brings significant overhead because of the network traffic 
            # being exchanged, but suffices for our small server.
            # Design note: we alternatively could have made non-blocking calls to 
            # conn.recv 

            data = conn.recv(4096)

            # eventually this will be replaced with processing logic
            print(data)

            if not user:
              # should have message type here or create account 
                print("TODO")
              # set user to username 

            while not users[user].deliver_now.empty():
                message = users[user].deliver_now.get()

                # in case of failure, put the message back on the queue to avoid
                # message drops. note that the message will now be at the end of 
                # the queue, so our server does not guarantee in-order message
                # delivery.
                try conn.sendall(message):
                    continue
                except Exception e:
                    users[user].deliver_now.put(message)




if __name__ == '__main__':

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("server is listening")

        while True:
            conn, addr = s.accept()
            start_new_thread(thread_func, (conn,))

