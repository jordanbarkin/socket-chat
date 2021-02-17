# socket-chat

For CS262 Assignment 1.

See `docs/` for how to get started with the app, the wire protocol writeup, and a journal of our progress.

## Server

`server.py` contains the code for the server. It relies on `userstate.py`, a library to handle user state on the server side.
The server has very little persistent storage (except a text file containing usernames), so these UserState objects are 
responsible for all server-side userstate, including login status and message queues. It also relies on `messages.py` our 
serialization and deserialization library. `messages.py` implements the specification described in `wire_protocol.md`. 

`users.txt` is the server's persistent storage. It is a text file containing all the usernames that the server has seen 
before. We've initialized it with the following usernames: [lukelavanya, luke, lavanya] (sorry Jordan)

## Client 

`client.py` contains the code for the client. The client is a command line interface that allows the user to interact 
with our chat application using keyboard input. The client also relies on `messages.py`for protocol serialization and deserialization.

## Testing

`integration_tests.py` contains testing code. Client input and output happens through wrapper functions that feed in 
simulated keyboard input in testing mode. The output function gathers the client's output and sends it to the testing
library, which thene xamines it for errors. 

`messages_unit_tests.py` contains unit tests for the serialization and deserialization library. 

To run all the tests at once, run `python3 client.py -t`
