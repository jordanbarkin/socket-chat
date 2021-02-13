import socket
import threading
import messages 
import select
import struct
import queue

HOST = "localhost"
PORT = 12345

message_queue = queue.Queue()
kill_socket = False

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

def ping(_):
    payload = messages.PingMessage()
    # TODO: Socket stuff
    print("Successfully reached server!")

# Logged out action functions

def program_quit(_):
    kill_socket = True
    exit("Goodbye!")

def login(sock):
    username = input("What is your username?: ")
    payload = messages.HereMessage(username)
    message_queue.put(payload.serialize())
    logged_in_loop(username)
    

def create_account(sock):
    username = input("What do you want your username to be?: ")
    payload = messages.CreateAccountMessage(username)
    message_queue.put(payload.serialize())
    logged_in_loop(username)


# Universal actions:
PING = 20

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
    payload = messages.AwayMessage()
    message_queue.put(payload.serialize())
    print("Logged out!")
    kill_socket = True
    return True

def chat_send():
    receiver = input("Who do you want to send the message to?: ")
    print("Write your message below and press 'enter' to send:")
    message = input()
    payload = messages.SendChatMessage(receiver, message)
    message_queue.put(payload.serialize())
    print("Message sent!")
    return False

def list_users():
    payload = messages.RequestUserListMessage()
    message_queue.put(payload.serialize())
    return False

def delete_account():
    payload = messages.DeleteAccountMessage()
    message_queue.put(payload.serialize())
    print("Account deleted!")
    kill_socket = True
    return True

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
}

def logged_in_loop(username):
    while True:
        print(f"You are logged in as {username}!")
        print(("What would you like to do now? Type '1' to log out, '2' to send a chat, "
            "'3' to list all available users, '4' to delete your account, and '5' to test connection. "))
        action = collect_user_input(LOGGED_IN_ACTIONS)
        if action == -1:
            continue
        logout = LOGGED_IN_ACTIONS[action]()
        if logout:
            return

def get_len(bytes):
    return struct.unpack("I", bytes[8:12])[0]
        
def socket_loop(sock):
    while True:
        if kill_socket:
            print("brb dying!")
            sock.close()
            return

        # First send any messages on the queue.
        while not message_queue.empty():
            message = message_queue.get()
            sock.send(message)

        # This look to see if any showed up.
        ready = select.select([sock], [], [], .5)
        if ready[0]:
            message = sock.recv(64)
            if message:
                message_len = get_len(message)
                while len(message) < message_len:
                    chunk = sock.recv(64)
                    message += chunk
                print(message)

def logged_out_loop():
    while True:
        print(("Welcome to Sooper Chat! Type '1' to log in, '2' to "
               "create an account, and '3' to quit."))
        action = collect_user_input(LOGGED_IN_ACTIONS)
        if action == -1:
            continue
        sock = None
        print("Establishing connection with server...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        print("Successfully connected to server!")
        threading.Thread(target=socket_loop, args=(sock,)).start()
        LOGGED_OUT_ACTIONS[action](sock)

if __name__ == "__main__":
    logged_out_loop()