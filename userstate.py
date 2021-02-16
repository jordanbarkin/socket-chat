#!/usr/bin/env python3

import queue

class UserState:
    '''This class encapsulates all server-side information about a particular user.

       @attribute self.here: bool
           True if the user is currently "here," as in has sent a "here" message, and
           has an open connection to the server.

       @attribute self.username: string
           Unique identifier for this user

       @attribute deliver_now: Queue
           queue of messages to be delivered immediately. These are messages that
           were received while the user was "here", and so should be delivered
           immediately according to the problem set specifications.

       @attribute deliver_later: Queue
           queue of messages to be delivered on-demand when the user is "here." These
           are messages that were received when the user was "away."

       @method add_message: message: (str, str) -> None
           add a message to the appropriate queue depending on whether or not the
           user is "here" Will be used by other threads to send messages to
           this user.
           @param: (sender, body) a tuple consisting of the sender's username and the
                   message body

       @notes
           Note that UserState has no memory of past messages. Both message queue
           contain only undelivered messages. Also note that the server has no
           persistent storage. This design decision was made to reduce developer time,
           but it comes at the cost of robustness. If we were extending this server,
           a historical record of messages and persistent storage would be high-
           priority features.
    '''

    def __init__(self, username: str):
        '''This method does not perform uniqueness checks on username. Uniqueness is
           the caller's responsibility.

           deliver_now and deliver_later are Queues and not lists because they need to
           support concurrent access by multiple threads. This user's thread may pop
           messages off the queues to deliver them, and other user threads may add
           messages to the queues.

           self.here and self.username are thread-safe because they are Python primitives
        '''
        self.here = False
        self.username = username
        self.deliver_now = queue.Queue()
        self.deliver_later = queue.Queue()

    def add_message(self, message: (str,str)):
        '''Other user threads call this method to add a message to this user's queue.
           Note a possible race condition: if self.here changes between method invocation
           and method exceution then the message may be pushed onto the wrong queue. We
           deem this race condition minor because the message will be still be delivered,
           it just may be delivered later than the sender will expect.
        '''
        if self.here:
            self.deliver_now.put(message)
        else:
            self.deliver_later.put(message)

    def login(self):
        self.here = True

    def logout(self):
        self.here = False

    def is_here(self):
        return self.here




