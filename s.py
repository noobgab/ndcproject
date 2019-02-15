import socket
import threading, Queue
from time import gmtime, strftime
import time
import hashlib

# Socket connection information
HOST = "127.0.0.1"
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST,PORT))

# Global Variables
buffer = ""
prefix = "!"
serverTitle = "No title"
hashTextCmd = ""

# Global Lists
currentConnections = list()
userList = list()
adminList = list()
adminList.append("admin")
commandList = ["help", "usercount", "servertime", "ping"]
errorList = {"TamperError":"Server had trouble receiving your message. Please try again"}

def parseInput(data, con):
    print str(data)
    data_split = data.split('-')
    if data_split[0][1:] == "cmd":
        cmd_extr = data_split[1]
        if cmd_extr == "help":
            lineHelp = "<cmd-server-help-Here is a list of commands: "
            for cmd in commandList:
                lineHelp += prefix + cmd + ", "
            lineHelp = lineHelp[0:-2]
            lineHelp += ">"
            hashTextCmd = hashlib.sha224(lineHelp).hexdigest()
            con.send(lineHelp + "-" + hashTextCmd)
        elif cmd_extr == "usercount":
            lineUsercount = "<cmd-server-usercount-There are "+str(len(userList))+" user(s) online>"
            hashTextCmd = hashlib.sha224(lineUsercount).hexdigest()
            con.send(lineUsercount + "-" + hashTextCmd)
        elif cmd_extr == "servertime":
            lineServertime = "<cmd-server-servertime-"+strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())+">"
            hashTextCmd = hashlib.sha224(lineServertime).hexdigest()
            con.send(lineServertime + "-" + hashTextCmd)
        elif cmd_extr == "ping":
            linePing = "<cmd-server-ping-pong>"
            hashTextCmd = hashlib.sha224(linePing).hexdigest()
            con.send(linePing + "-" + hashTextCmd)
        elif cmd_extr == "quit":
            con.send("<cmd-confirm-user-quit>")
            con.shutdown(socket.SHUT_RD)
    elif data_split[0][1:] == "msg":
        for singleClient in currentConnections:
            singleClient.send(data)
        """
        hashCheckMsg = hashlib.sha224(data_split[3][0:-1]).hexdigest()
        if hashCheckMsg == data_split[2]:
            lineMsg = str(data)
            hashTextCmd = hashlib.sha224(lineMsg).hexdigest()
            for singleClient in currentConnections:
				singleClient.send(lineMsg + "-" + hashTextCmd)
        else:
            lineMsgError = "<msg-server-error-" + errorList["TemperError"] + ">"
            hashTextCmd = hashlib.sha224(lineMsgError).hexdigest()
            con.send(lineMsgError + "-" + hashTextCmd)
            print "TamperError"
            print "Original hash: " + data_split[2]
            print "Tampered hash: " + hashCheck
        """

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
        print "Checking username: \"" + str(checkstr[4][0:-1]) + "\""
        if checkstr[0] == "<cmd" and checkstr[2] == "namechange":
            usr = checkstr[4][0:-1]
            if checkstr[3] == hashlib.sha224(usr).hexdigest():
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
                        hashTextCmd = hashlib.sha224(usr+" has joined the chat").hexdigest()
                        typeMsg = strftime("%H:%M:%S", gmtime())
                        if singleClient == con:
                            typeMsg = "startup"
                        
                        lineMsgJoin = "<msg-server-"+typeMsg+"-"+hashTextCmd+"-"+usr+" has joined the chat>"
                        singleClient.send(lineMsgJoin)
            else:
                con.send("<cmd-confirm-false>");

    while 1:
        data = con.recv(1024)
        parseInput(data, con)

while 1:
    s.listen(1)
    con, addr = s.accept()

    t = threading.Thread(target=manageConnection, args=(con, addr))
    t.start()