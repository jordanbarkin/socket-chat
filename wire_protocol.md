
# Wire Protocol Description (Version 1)

Each message in our wire protocol will have the following fields. Field names in **bold** and lengths in bytes *italicized*.

**version number** *4* | **message type** *4* | **message payload** *len*

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
  * **empty** *0*
* Here (Type = 1)
  * Used to indicate presence of a client. Clients marked as "here" will recieve messages as soon as they are sent.
  * **username_len** *4* | **username** *len* 

* Create Account (Type = 2)
  * Used to create a new user account. Note that we don't have a password requirement for here or create account. This chat
    application is very insecure.
  * **username_len** *4* | **username** *len*
  
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
* Poll (Type = 8)
  * Used to constantly poll the server and notify of client liveness
  * **empty** *0*

### Server to Client Messages
* Pong (Type = 9)
  * Response to ping
  * **empty** *0*
* Undelivered Messages (Type = 10)
  * List of underlivered messages recieved when client is "away"
  * **number of messages** *4* | **message1** | **message2** | ...
  * Each message is structured as 
  **sender length** *4* | **sender username** *len* | **body length** *4* | **message body** *len*
* Response to poll (Type = 11)
  * Contains any undelivered messages recieved when client is "here"
  * Same structure as undelivered messages
    
    
