import socket
import threading
import messages 
import select
import struct
import queue
import time

HOST = "localhost"
PORT = 12345

message_queue = queue.Queue()
is_connected = False
logged_in = False
username = None

# Helper functions

'''
    @param valid_actions: A dictionary mapping action code numbers to
    their associated functions

    @returns: -1 if there is an error and the action code if the input is
    valid
'''
def collect_user_input(valid_actions):
    try:
        action = int(input().strip())
    except ValueError:
        print("It looks like you did not input an integer. Try again!\n")
        return -1
    if action not in valid_actions:
        print("It looks like you input an invalid number. Try again")
        return -1
    return action

# Universal action functions

def ping():
    payload = messages.PingMessage()
    message_queue.put(payload.serialize())

# Logged out action functions

def program_quit():
    exit("Goodbye!")

def login():
    global logged_in
    global username
    local_username = input("What is your username?: ")
    payload = messages.HereMessage(local_username)
    message_queue.put(payload.serialize())
    logged_in = True
    username = local_username
    

def create_account():
    global logged_in
    global username
    local_username = input("What do you want your username to be?: ")
    payload = messages.CreateAccountMessage(local_username)
    message_queue.put(payload.serialize())
    logged_in = True
    time.sleep(.5)
    username = local_username


# Universal actions:
PING = 9

# Logged out actions
LOGIN = 1
CREATE_ACCOUNT = 2
QUIT = 3

LOGGED_OUT_ACTIONS = {
    LOGIN: login,
    CREATE_ACCOUNT: create_account,
    QUIT: program_quit,
    PING: ping
}



# Logged in action functions

def logout():
    global logged_in
    payload = messages.AwayMessage()
    message_queue.put(payload.serialize())
    print("Logged out!")
    logged_in = False

def chat_send():
    receiver = input("Who do you want to send the message to?: ").strip()
    print("Write your message below and press 'enter' to send:")
    message = input()
    payload = messages.SendChatMessage(receiver, message)
    message_queue.put(payload.serialize())
    print("Message sent!")

def list_users():
    payload = messages.RequestUserListMessage()
    message_queue.put(payload.serialize())
    

def delete_account():
    global logged_in
    payload = messages.DeleteAccountMessage()
    message_queue.put(payload.serialize())
    print("Account deleted!")
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

def logged_in_sequence():
    global username
    print(f"You are logged in as {username}!")
    print(("What would you like to do now? Type '1' to log out, '2' to send a chat, "
        "'3' to list all available users, '4' to delete your account, '5' to receive undelivered messages, and '9' to test connection. "))
    action = collect_user_input(LOGGED_IN_ACTIONS)
    if action != -1:
        LOGGED_IN_ACTIONS[action]()

def socket_loop(sock):
    global logged_in
    global is_connected
    while True:

        # First send any messages on the queue.
        while not message_queue.empty():
            message = message_queue.get()
            sock.send(message)

        # Look to see if any messages showed up.
        ready = select.select([sock], [], [], .5)
        if ready[0]:
            try:
                message = sock.recv(64)
            except OSError as e:
                sock.close()
                is_connected = False
                logged_in = False
                print("Failed to receive data. Resetting connection.")
                return

            if message:
                message_len = messages.extract_length(message)
                while len(message) < message_len:
                    try:
                        chunk = sock.recv(64)
                    except OSError:
                        sock.close()
                        is_connected = False
                        logged_in = False
                        print("Failed to receive data. Resetting connection.")
                        return
                    message += chunk

                try:
                    message_object = messages.deserialize_message(message)
                except:
                    print("Invalid message received. Closing program.")
                    sock.close()
                    is_connected = False
                    logged_in = False
                    return 

                message_type = type(message_object)
                if message_type == messages.PongMessage:
                    print("Pong message received!")
                elif message_type == messages.UserListResponseMessage:
                    print("These are the users!:")
                    print(message_object.user_list)
                    print()
                elif message_type == messages.DeliverMessage:
                    for message in message_object.message_list:
                        sender, body = message
                        print(f"Message from {sender}:")
                        print(body)
                        print()
                else:
                    # Error message
                    error_message = message_object.error_message
                    print("Error!", error_message)
                    logged_in = False
                print(message)


def logged_out():
    global is_connected
    if not is_connected:
        print("Establishing connection with server...")
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
        except OSError:
            print("Failure to connect!")
            program_quit()
        is_connected = True
        threading.Thread(target=socket_loop, args=(sock,)).start()
        print("Successfully connected to server!")
    print()
    print(("Welcome to Sooper Chat! Type '1' to log in, '2' to "
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
            logged_out()

if __name__ == "__main__":
    main()
