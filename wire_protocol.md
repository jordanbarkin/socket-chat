
# Wire Protocol Description (Version 1)

Each message in our wire protocol will have the following fields. Field lengths are specified below field name.


|version number | message type | payload len | message payload|
-------------------------------------------------------------
|(4 bytes)      |(4 bytes)     | (4 bytes)   | (len bytes)|



## Version Number

This description is for Version 1 of our wire protocol.

## Message Type

Deserializers should interpret this field as a 4-byte integer. Message types are described below.

## Message Payload

Different message types may have different message payloads. Messages are grouped into client to server messages and 
server to client messages. 

### Client to Server Messages

* Ping (Type = 0)
  * Used for debugging purposes to check liveness
  * Empty Payload
* Here (Type = 1)
  * Used to indicate presence of a client. Clients marked as "here" will recieve messages as soon as they are sent.
  * -------------------------------
    username_len   | username     | 
    (4 bytes)      |(len bytes)   | 
    -------------------------------
* Create Account (Type = 2)
  * Used to create a new user account. Note that we don't have a password requirement for here or create account. This chat
    application is very insecure.
  * -------------------------------
    username_len   | username     | 
    (4 bytes)      |(len bytes)   | 
    -------------------------------
* Away (Type = 3)
  * Used to terminate a session with the server. Server will close the connection and mark the client as "away." Messages sent 
    during an "away" period will be recieved when the client is "here" again.
  * Empty payload
* Chat Send (Type = 4)
  * Used to send a chat to another user. 
  * ----------------------------------------------------------
    reciever_len | reciever username | body_len | message body
    (4 bytes)    |(len bytes)        | (4 bytes)| (len bytes)
    ---------------------------------------------------------
* List Users (Type = 5)
  * Used to ask server for list of user accounts
  * Empty payload
* Delete Account (Type = 6)
  * Delete the current "here" account. Server does nothing if the client is not "here." Note that the server is stateful.
  * Empty payload
* Show Undelivered Messages (Type = 7)
  * Ask server to send messages delivered while ths currently "here" user was "away"
  * Empty payload
* Poll (Type = 8)
  * Used to constantly poll the server and notify of client liveness
  * Empty payload

### Server to Client Messages

    
