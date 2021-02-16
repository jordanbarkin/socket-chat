# Getting Started

## Running the Server

To start the server, run the command

```python3 server.py```

By default, the server runs on localhost on port 12345, so the client and server will need to be running on the same machine. 


## Running the client 

To start the client, run the command

```python3 client.py```

### Command Line Arguments:

**-server** defaults to localhost

**-port** defaults to 12345

**-t** enable testing mode, described below 

## Testing

**Integration Tests** These test end-to-end client to server and server to client interactions. To get started, 
run the server as described above, and then run the client with the '-t' flag as follows:

```python3 client.py -t```
