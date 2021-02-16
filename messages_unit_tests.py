from messages import *

# We create one of each type of message and make sure that its serialization
# deserializes to an identical representation
def run_test(test_object):
    success = (deserialize_message(test_object.serialize()) == test_object)

    if success:
        print("Test succeeded: " + str(type(test_object)))
    else:
        print("Test FAILED: " + str(type(test_object)))

def test_all():
    test_message_objects = [
        PingMessage(),
        PongMessage(),
        HereMessage("test_username"),
        CreateAccountMessage("test_username"),
        AwayMessage(),
        SendChatMessage("test_username_longer", "Hi there!"),
        RequestUserListMessage(),
        DeleteAccountMessage(),
        DeliverMessage([("recip1", "message1"), ("recip2", "hey here's a longer message for the fun of it.")]),
        UserListResponseMessage(["user1", "user2", "lavanya", "jordan", "luke"]),
        ErrorMessage("Everything broke! Halp!")
    ]

    for test_object in test_message_objects:
        run_test(test_object)
