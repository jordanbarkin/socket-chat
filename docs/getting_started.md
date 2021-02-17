# Getting Started

The client and server both require Python 3.7+ and only make use of packages in the standard library. 

## Running the Server

To start the server, run the command

```python3 server.py```

By default, the server runs on localhost on port 12345, so the client and server will need to be running on the same machine.

### Optional Server Command Line Arguments:

**-ip** defaults to localhost

**-port** defaults to 12345

## Running the client

To start the client, run the command

```python3 client.py```

### Optional Client Command Line Arguments:

**-server** defaults to localhost

**-port** defaults to 12345

**-t** runs test suite instead of launching the user-facing client. 

## Testing

Running with the test flag runs unit tests and integration tests.

**Unit Tests** These test that for each type of message defined in messages.py, the result of deserializing the serialization of the message is identical to the original message. Equality on messages is defined in each message's class.

**Integration Tests** These test end-to-end client to server and server to client interactions.

To run all tests, run the server as described above, and then run the client with the '-t' flag as follows:

```python3 client.py -t```
