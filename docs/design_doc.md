# Design Decisions and Explanations

**Decision #1:** On the server, we represent user state with a boolean flag `here`, their `username` as a string, a thread-safe queue called `deliver_now`, and another thread-safe queue `deliver_later`. 

Messages sent to the server get put in the `deliver_now` queue if the recipient is logged in and has an established a connection with the server, and they get put in the `deliver_later` queue if the recipent does not. The `deliver_now` messages get sent as soon as soon as a worker thread is able to, and the `deliver_later` messages get sent once a user requests them. We originally considered using a single queue for messages the user is supposed to receive, and marking them with a flag to represent if they should be delivered now or later. However, if we had done this, we would have had to filter through the queue to gather the appropriate messages. The dual-queue design allows the server to just check a single queue when it is supposed to deliver a message.

**Decision #2:** We used a dictionary to keep track of each user's state on the server side. This dictionary mapped ther user's username to their state.

Using a dictionary gives us expected O(1) lookup time when a server thread needs to access user state. Further, dictionaries with string keys are atomic in Python, so we did not have to worry about conflicts between threads accessing this global data structure.

**Decision #3:** We use a separate thread for each connection to the server.

On the server side, we considered using a global processing thread to handle all of the connections. With this method, we would have to use some type of global data structure to keep track of state for each connection, as well as the connection itself. Whenever a message came in to any of the sockets, we could deserialize the message then handle it. 

We ultimately decided that having a thread for each connection would make it easier to keep track of per-connection state and maintain multiple connections. Because of the atomic nature of our global data structures, we were not worried about inconsistent state or deadlock. If we had to scale larger, though, this design choice could present problems.

**Decision #4:** The client and server both wait for each other's messages for half a second, then send any requests that need to be sent, then go back to waiting.

We originally considered having the client and server ping each other constantly for a new message. This, however, would have the downside of overloading the network with requests. It would also require us to build a request/response protocol similar to HTTP which would, in many ways, defeat the ability to send messages instantly. Perhaps a better design would have been to create a scheme on top of sockets similar to HTTP for many of our requests, and then use raw sockets for instant message functionality. However, given the scale of this project, we figured that using raw sockets was sufficient.

**Decision #5:** We kept track of the connection's username on the server side.

Building off of decisions 3 & 4, We originally considered having the client send its username in each request where that was needed. This would have the benefit of having a "stateless" chat API. However, because we have persistent socket connections, allowing for "instant" messageing capability, sending state in each request becomes redundant, so we decided not to include the username in each outgoing message from the client unless it was necessary.

**Decision #6:** We used a shared library for serialization and deserialization between raw bytes on the wire and Python objects.

By building this shared library, once our client or server received bytes from the socket, it could then convert it into the appropriate Python object and use an if/elif chain to determine which action to take based on the type of that object. Because the library was shared, the client and server could know that they would be sending and receiving the same objects on both sides.

**Decision #7:** We included the version number, message type, and  message length (following the first 12 bytes) -- each encoded as 4 byte little-endian integers -- in the first 12 bytes of the transmission.

The version length allows us to ensure that the server and client are using the same protocol. The message type helps our shared library determine how to parse the whole message. The message length lets the receiver know how many bytes to wait for.

**Decision #8:** The client uses one thread for handling the socket connection, and another for handling user input/interface.

Python threads block when awaiting input from the user. If we were to use one thread to handle user input and handle networking, we could not receive messages while awaiting user input. This would violate the requirement that users are able to receive messages instantly. Because sockets are not thread-safe in python, this means that we cannot send transmissions over the socket directly from the thread that received user input, because the other thread is waiting to receive messages from that same socket. To work around this issue, we had the user input thread pass the message to a thread-safe global queue. The socket thread would wait for half a second to receive messages on the socket, handle any messages that came in, then check the queue to see if any messages needed to be sent. If there were messages on the queue, it would send those over the socket then continue awaiting messages.

**Decision #9:** We only included support for the server running on `localhost`.

In development, we were able to have the server work over UPnP to support running the chat app on a publicly-reachable server. However, support for this was finnicky, so we figured it would be best to only officially support running the app on `localhost`. 