
# Wire Protocol Description (Version 1)

This protocol is implemented in messages.py, which provides encoding and decoding for each message type.

Each message in our wire protocol will have the following fields. Field names in **bold** and lengths in bytes *italicized*.

**version number** *4* | **message type** *4* | **message payload len** *4* | **message payload** *len*

## Version Number

This description is for Version 1 of our wire protocol.

## Message Type

Deserializers should interpret this field as a 4-byte integer. Message types are described below.

## Message Len

The total length of the payload. That is, how many more bytes total must be read *after* the first 12 read in the header.

## Message Payload

Different message types may have different message payloads. Messages are grouped into client to server messages and
server to client messages.


### Client to Server Messages

* Ping (Type = 0)
  * Used for debugging purposes to check liveness
  * **empty**
* Here (Type = 1)
  * Used to indicate presence of a client. Clients marked as "here" will recieve messages as soon as they are sent.
  * **username length** *4* | **username** *len*
* Create Account (Type = 2)
  * Used to create a new user account. Note that we don't have a password requirement for here or create account. This chat
    application is very insecure.
  * **username length** *4* | **username** *len*
* Away (Type = 3)
  * Used to terminate a session with the server. Server will close the connection and mark the client as "away." Messages sent
    during an "away" period will be recieved when the client is "here" again.
  * **empty** *0*
* Chat Send (Type = 4)
  * Used to send a chat to another user.
  * **reciever length** *4* | **reciever username** *len* | **body length** *4* | **message body** *len*
* List Users (Type = 5)
  * Used to ask server for list of user accounts
  * **empty** *0*
* Delete Account (Type = 6)
  * Delete the current "here" account. Server does nothing if the client is not "here." Note that the server is stateful.
  * **empty** *0*
* Show Undelivered Messages (Type = 7)
  * Ask server to send messages delivered while ths currently "here" user was "away"
  * **empty** *0*

### Server to Client Messages
* Pong (Type = 9)
  * Response to ping
  * **empty** *0*
* Messages Send (Type = 10)
  * List of messages in respose to a new message or a Show Undelivered Messages request
  * **number of messages** *4* | **message1** | **message2** | ...
  * Each message is structured as
  **sender length** *4* | **sender username** *len* | **body length** *4* | **message body** *len*
* List of Users (Type = 11)
  * List of users in response to a list users message
  * **number of users** *4* | **user1** | **user2** | .......
  * Each user is structured as
  * **username length** *4* | **username** *len*
* Error (Type = 12)
  * Error message
  * **error length** *4* | **error message** *len*

##  Notes

- Strings are encoded in UTF-8.
- We use the default big endian byte order on the wire.
- All length fields store length in bytes of the subsequent data.
