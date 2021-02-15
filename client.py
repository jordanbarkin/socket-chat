import socket
import threading
import messages
import select
import queue
import time
import sys
from integration_tests import *

# Configuration
HOST = "localhost"
PORT = 12345
TESTING = False

# Global client state
message_queue = queue.Queue()
is_connected = False
logged_in = False
username = None

# Helper functions

'''
    wrapper function for testing purposes. same interface as input()
'''
def input_wrapped(message=None):
    if TESTING:
        return input_test()
    elif message:
        return input(message)
    else:
        return input()

'''
    wrapped function for testing purposes. same interface as print()
'''
def print_wrapped(message=""):
    if TESTING:
        return test_output(message)
    else:
        return print(message)

'''
    @param valid_actions: A dictionary mapping action code numbers to
    their associated functions
    @returns: -1 if there is an error and the action code if the input is
    valid
'''
def collect_user_input(valid_actions):
    try:
        action = int(input_wrapped().strip())
    except ValueError:
        print_wrapped("It looks like you did not input an integer. Try again!\n")
        return -1
    if action not in valid_actions:
        print_wrapped("It looks like you input an invalid number. Try again")
        return -1
    return action

# Handlers for functions that you can use when logged in or out

def ping():
    payload = messages.PingMessage()
    message_queue.put(payload.serialize())

# Handlers for requests from the user when logged out

def program_quit():
    exit("Goodbye!")

def login():
    global logged_in
    global username
    local_username = input_wrapped("What is your username?: ")
    payload = messages.HereMessage(local_username)
    message_queue.put(payload.serialize())
    logged_in = True
    username = local_username


def create_account():
    global logged_in
    global username
    local_username = input_wrapped("What do you want your username to be?: ")
    payload = messages.CreateAccountMessage(local_username)
    message_queue.put(payload.serialize())
    logged_in = True
    time.sleep(.5)
    username = local_username

# Universal actions:
PING           = 9

# Logged out actions
LOGIN          = 1
CREATE_ACCOUNT = 2
QUIT           = 3


LOGGED_OUT_ACTIONS = {
    LOGIN: login,
    CREATE_ACCOUNT: create_account,
    QUIT: program_quit,
    PING: ping
}

# Handlers for requests from the user when logged in

def logout():
    global logged_in
    payload = messages.AwayMessage()
    message_queue.put(payload.serialize())
    print_wrapped("Logged out!")
    logged_in = False

def chat_send():
    receiver = input_wrapped("Who do you want to send the message to?: ").strip()
    print_wrapped("Write your message below and press 'enter' to send:")
    message = input_wrapped()
    payload = messages.SendChatMessage(receiver, message)
    message_queue.put(payload.serialize())
    print_wrapped("Message sent!")

def list_users():
    payload = messages.RequestUserListMessage()
    message_queue.put(payload.serialize())

def delete_account():
    global logged_in
    payload = messages.DeleteAccountMessage()
    message_queue.put(payload.serialize())
    print_wrapped("Account deleted!")
    logged_in = False

def show_messages():
    payload = messages.ShowUndeliveredMessage()
    message_queue.put(payload.serialize())

# Logged in actions
LOGOUT = 1
CHAT_SEND = 2
LIST_USERS = 3
DELETE_ACCOUNT = 4
SHOW_MESSAGES = 5

LOGGED_IN_ACTIONS = {
    LOGOUT: logout,
    CHAT_SEND: chat_send,
    LIST_USERS: list_users,
    DELETE_ACCOUNT: delete_account,
    SHOW_MESSAGES: show_messages,
    PING: ping
}

# The user flow when logged in.

def logged_in_sequence():
    global username
    print_wrapped(f"You are logged in as " + username + "!")
    print_wrapped(("What would you like to do now? Type '1' to log out, '2' to send a chat, "
        "'3' to list all available users, '4' to delete your account, '5' to receive undelivered messages, and '9' to test connection. "))
    action = collect_user_input(LOGGED_IN_ACTIONS)
    if action != -1:
        LOGGED_IN_ACTIONS[action]()

def logout(sock):
    sock.close()
    is_connected = False
    logged_in = False

def read_message_bytes(sock):
    # Look to see if any messages showed up.
    ready = select.select([sock], [], [], .5)

    # no message received
    if not ready[0]:
        return None

    # read the first 64 bytes
    try:
        message = sock.recv(64)
    except OSError as e:
        logout(sock)
        print_wrapped("Failed to receive data. Resetting connection.")
        return None

    # if we haven't received a message, nothing to do
    if not message:
        return None

    # read the rest of the message
    message_len = messages.extract_length(message)
    while len(message) < message_len:
        try:
            chunk = sock.recv(64)
        except OSError:
            logout(sock)
            print_wrapped("Failed to receive data. Resetting connection.")
            return None
        message += chunk

    return message

# The listener thread runs this loop, checking for and handling
# any new communication from the server.
def socket_loop(sock):
    global logged_in
    global is_connected

    while True:
        # First send any messages on the queue to the server.
        while not message_queue.empty():
            message = message_queue.get()
            sock.send(message)

        message_bytes = read_message_bytes(sock)

        # Nothing new from the server.
        if not message_bytes:
            continue

        try:
            message_object = messages.deserialize_message(message_bytes)
        except Exception as e:
            print_wrapped("Failed to deserialize message." + str(e.message))
            print_wrapped("Invalid message received. Closing program.")
            logout(sock)
            return

        # Handle messages from server, depending on type.

        message_type = type(message_object)

        # received response to a ping
        if message_type == messages.PongMessage:
            print_wrapped("Pong message received!")

        # received a response to a request for a list of users
        elif message_type == messages.UserListResponseMessage:
            print_wrapped("These are the users!:")
            print_wrapped(message_object.user_list)
            print_wrapped()

        # received messages
        elif message_type == messages.DeliverMessage:
            for message in message_object.message_list:
                sender, body = message
                print_wrapped(f"Message from " + sender + ":")
                print_wrapped(body)
                print_wrapped()

        # received an error
        elif message_type == messages.ErrorMessage:
            print_wrapped("Error received: " + str(message_object.error_message))
            print_wrapped("If problems persist, please log out and log back in.")

        # Server is sending nonsense.
        else:
            print("Invalid message object.")

# The user flow when logged out.
def logged_out_sequence():
    global is_connected
    if not is_connected:
        print_wrapped("Establishing connection with server...")
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
        except OSError:
            print_wrapped("Failure to connect!")
            program_quit()
        is_connected = True
        threading.Thread(target=socket_loop, args=(sock,)).start()
        print_wrapped("Successfully connected to server!")
    print_wrapped()
    print_wrapped(("Welcome to Sooper Chat! Type '1' to log in, '2' to "
            "create an account, '3' to quit, and '9' to ping (test connection)."))
    action = collect_user_input(LOGGED_IN_ACTIONS)
    if action != -1:
        LOGGED_OUT_ACTIONS[action]()


def main():
    global logged_in
    global is_connected

    while True:
        time.sleep(1)

        if logged_in:
            logged_in_sequence()
        else:
            logged_out_sequence()

if __name__ == "__main__":
    # enable test mode if -t flag is set
    if (len(sys.argv) > 1 and sys.argv[1] == "-t"):
        TESTING = True

    main()
