import socket
import threading
from time import gmtime, strftime
import time
import hashlib

HOST = "127.0.0.1"
PORT = 50007

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

prefix = "!"
username = ""

def setupUser(socket):
    global username
    nameDone = False

    while nameDone == False:
        username = raw_input("Enter a username: ")
        socket.sendall("<cmd-startup-namechange-"+str(username)+">")

        data = socket.recv(1024)

        if "<cmd-confirm-true" in data:
            print "Username has been set to: " + username
            cmd_split = data.split('-')
            print "Welcome to the chat: " + cmd_split[3][0:-1]
            nameDone = True
        else:
            print "Error setting username. Try again..."

def readInput(user, socket):
    while 1:
        text = raw_input()
        hashText = hashlib.sha224(text).hexdigest()
        if prefix+"help" in text:
            line = "<cmd-help-"+user+">"
        elif prefix+"usercount" in text:
            line = "<cmd-usercount-"+user+">"
        elif prefix+"servertime" in text:
            line = "<cmd-servertime-"+user+">"
        elif prefix+"ping" in text:
		    line = "<cmd-ping-"+user+">"
        else:
            line = "<msg-" + user + "-" + hashText + "-" + text + ">"
        socket.sendall(line)

def readData(user, socket):
    while 1:
        data = socket.recv(1024)
        hashCheck = hashlib.sha224(data).hexdigest()
        data_split = data.split('-')
        if data_split[1] == "confirm":
            if hashCheck == data_split[4]:
                print "[" + strftime("%H:%M:%S", gmtime()) + "] " + data_split[1] + ": " + data_split[3][0:-1]
        else:
		    print "[" + strftime("%H:%M:%S", gmtime()) + "] " + data_split[1] + ": " + data_split[3][0:-1]

setupUser(s)

t = threading.Thread(target=readInput, args=(username, s))
t.start()

t = threading.Thread(target=readData, args=(username, s))
t.start()