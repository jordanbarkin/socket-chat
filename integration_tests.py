#!/usr/bin/env python3

'''
    helper functions for integration testing. these functions simulate keyboard input
    to check each of the required actions specified in wire_protocol.md
'''

import os 

# useful constants 
MAGIC_WORD = "FOOBAR"
uname1 = "lavanya"
uname2 = "luke"

# global variables to keep track of the current test
test_counter = 1
counter = 0
output = []
looking_for_message = 0

# this function checks the client's output for an error condition corresponding to num
def check_for_error(num):
    if num == 0:
        return
    
    output_string = "".join([el for sublist in output for el in sublist])
    failed = False
    # checking for general errors
    if looking_for_message == 0:
        failed = output_string.find("error") != -1
    # looking for message content
    elif looking_for_message == 1:
        failed = output_string.find(MAGIC_WORD) == -1
    # looking for user list
    elif looking_for_message == 2:
        failed = (output_string.find(uname2) == -1 or output_string.find(uname1) == -1)

    if failed:
        print("test "+str(num)+" failed. aborting")
        os._exit(1)
    else:
        print("test "+str(num)+" passed")


# Account creation from scratch
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

# Testing the "away" functionality
def test2():
    global test_counter
    if counter == 0:
        test_counter += 1
        return "1"

# Testing the "here" functionality
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

# Send a message to yourself and see if it's recieved
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
        return uname1
    if counter == 3:
        counter += 1
        return "2"
    if counter == 4:
        counter += 1
        return uname1
    if counter == 5:
        counter = 0
        test_counter += 1
        looking_for_message = 1
        return MAGIC_WORD

# Test that the user list currently grabs all users
def test5():
    global test_counter
    if counter == 0:
        test_counter += 1
        looking_for_message = 2
        return "3"

# Delete your current account
def test6():
    global test_counter
    if counter == 0:
        test_counter += 1
        looking_for_message = 0
        return "4"

# set up for test 7 by remaking the account
def test7():
    global test_counter
    global counter
    if counter == 0:
        counter += 1
        return "2"
    if counter == 1:
        counter += 1 
        return uname1
    if counter == 2:
        counter = 0
        test_counter += 1
        return "1"

# Test on-demand message delivery
def test8():
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

# returns simulated input for testing purposes
def input_test():
    global test_counter
    global counter
    
    if counter == 0:
        check_for_error(test_counter - 1)
    try:
        return globals()["test"+str(test_counter)]()
    except:
        print("Done testing! :)))))")
        os._exit(1)

# collects output 
def test_output(message=""):
    global output
    output.append(message)

