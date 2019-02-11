import socket
import threading, Queue
from time import gmtime, strftime
import time

# Socket connection information
HOST = "127.0.0.1"
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST,PORT))

# Global Variables
buffer = ""
prefix = "!"
serverTitle = "No Title"

# Global Lists
currentConnections = list()
userList = list()
adminList = list()
adminList.append("admin")
commandList = ["help", "usercount", "servertime"]

def parseInput(data, con):
    print str(data)
    data_split = data.split('-')
    if data_split[0][1:] == "cmd":
        cmd_extr = data_split[1]
        if cmd_extr == "help":
            line = "<cmd-help-Here is a list of commands: "
            for cmd in commandList:
                line += "!" + cmd + ", "
            line += ">"
            line = line[0:-2]
            con.send(line)
        elif cmd_extr == "usercount":
            con.send("<cmd-server-There are "+str(len(userList))+" user(s) online>")
        elif cmd_extr == "servertime":
            con.send("<cmd-server-"+strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())+">")
    elif data_split[0][1:] == "msg":
        for singleClient in currentConnections:
            singleClient.send(str(data))


def manageConnection(con, addr):
    global currentConnections
    global serverTitle
    global userList

    print "Connected by: " + str(addr)
    currentConnections.append(con)

    nameDone = False
    while nameDone == False:
        data = con.recv(1024)
        checkstr = data.split("-")
        print "Checking username: \"" + str(checkstr[2][0:-1]) + "\""
        if checkstr[0] == "<cmd" and checkstr[1] == "namechange":
            usr = checkstr[2][0:-1]
            try:
                userList.index(usr)
                print "Username declined"
                con.send("<cmd-confirm-false>")
            except ValueError as ve:
                userList.append(usr)
                nameDone = True
                print "Username accepted"
                con.send("<cmd-confirm-true-"+serverTitle+">")
                for singleClient in currentConnections:
                    singleClient.send("<msg-server-"+usr+" has joined the chat>")

    while 1:
        data = con.recv(1024)
        parseInput(data, con)

while 1:
    s.listen(1)
    con, addr = s.accept()

    t = threading.Thread(target=manageConnection, args=(con, addr))
    t.start()