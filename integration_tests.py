#!/usr/bin/env python3

'''
    helper functions for integration testing. these functions mimic keyboard
    input for testing purposes.
'''
MAGIC_WORD = "FOOBAR"
uname1 = "lavanya"
uname2 = "luke"

test_counter = 1
counter = 0
output = []
looking_for_message = 0

def check_for_error(num):
    failed = False
    if looking_for_message == 0:
        failed = "".join(output).find("error") != -1
    elif looking_for_message == 1:
        failed = "".join(output).find(MAGIC_WORD) == -1
    elif looking_for_message == 2:
        failed = ("".join(output).find(uname1) == -1 or "".join(output).find(uname1) == -1)
    if failed:
        print(output)
        print("test "+str(num)+" failed. aborting")
        exit()
    else:
        print("test "+str(num)+" passed")

# test account creation
def test1():
    global counter
    global test_counter
    if counter == 0:
        counter += 1
        return "2"
    if counter == 1:
        counter = 0
        test_counter += 1
        return uname1

# test away 
def test2():
    global test_counter
    if counter == 0:
        test_counter += 1
        return "1"

# test here
def test3():
    global counter
    global test_counter
    if counter == 0:
        counter += 1
        return "1"
    if counter == 1:
        counter = 0
        test_counter += 1
        return uname1

# test message send
def test4():
    global counter 
    global test_counter
    if counter == 0:
        counter += 1
        return "1"
    if counter == 1:
        counter += 1
        return "2"
    if counter == 2:
        counter += 1
        return uname2
    if counter == 3:
        counter += 1
        return "2"
    if counter == 4:
        counter = 0
        test_counter += 1
        looking_for_message = 1
        return MAGIC_WORD

# test user list
def test5():
    global test_counter
    if counter == 0:
        test_counter += 1
        looking_for_message = 2
        return "3"

# test delete account
def test6():
    global test_counter
    if counter == 0:
        test_counter += 1
        looking_for_message = 0
        return "4"

# test messages delivered on-demand
def test7():
    global test_counter
    global counter 
    if counter == 0:
        counter += 1
        return "2"
    if counter == 1:
        counter += 1
        return uname2
    if counter == 2:
        counter += 1
        return "2"
    if counter == 3:
        counter += 1
        return uname1
    if counter == 4:
        counter += 1
        return MAGIC_WORD
    if counter == 5:
        counter += 1
        return "1"
    if counter == 6:
        counter += 1
        return "1"
    if counter == 7:
        counter += 1
        return uname1
    if counter == 8:
        counter = 0
        test_counter += 1
        looking_for_message = 1
        return "5"

def input_test():
    global test_counter
    global counter
    
    if counter == 0:
        check_for_error(test_counter - 1)
    return globals()["test"+str(test_counter)]()

def test_output(message=""):
    global output
    output.append(message)

