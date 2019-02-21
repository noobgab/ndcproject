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
commandList = ["help", "usercount", "servertime", "ping", "quit"]

errorList = {
    "TamperError": "Server had trouble receiving your message. Please try again",
    "InvalidCommandError": "This command does not exist, please type !help to get the list of available commands"
}

cmd_hex_disct = {
    "help": hashlib.sha224("help").hexdigest(),
    "usercount": hashlib.sha224("usercount").hexdigest(),
    "servertime": hashlib.sha224("servertime").hexdigest(),
    "ping": hashlib.sha224("ping").hexdigest(),
    "quit": hashlib.sha224("quit").hexdigest()
}
#<type-author-timestamp-hash-content>

def getServerTime():
    return strftime("%H:%M:%S", gmtime())

def getHash(str):
    return hashlib.sha224(str).hexdigest()

def parseInput(data, con):
    print str(data)
    data_split = data.split('-')
    if data_split[0][1:] == "cmd":
        cmd_extr = data_split[1]
        dataTamp = False
        if cmd_extr == "help":
            if data_split[3] == cmd_hex_disct["help"]:
                lineStr = "Here is a list of available commands: "
                for cmd in commandList:
                    lineStr += prefix + cmd + ", "
                lineStr = lineStr[0:-2]

                line = "<cmd-server-"+getServerTime()+"-"+getHash(lineStr)+"-"+lineStr+">"
                con.send(line)
            else:
                dataTamp = True
        elif cmd_extr == "usercount":
            if data_split[3] == cmd_hex_disct["usercount"]:
                lineStr = "There are "+str(len(userList))+" user(s) online"
                line = "<cmd-server-"+getServerTime()+"-"+getHash(lineStr)+"-"+lineStr+">"
                con.send(line)
            else:
                dataTamp = True
        elif cmd_extr == "servertime":
            if data_split[3] == cmd_hex_disct["servertime"]:
                lineStr = "The current server time is: " + getServerTime()
                line = "<cmd-server-"+getServerTime()+"-"+getHash(lineStr)+"-"+lineStr+">"
                con.send(line)
            else:
                dataTamp = True
        elif cmd_extr == "ping":
            if data_split[3] == cmd_hex_disct["ping"]:
                lineStr = "Pong!"
                line = "<cmd-server-"+getServerTime()+"-"+getHash(lineStr)+"-"+lineStr+">"
                con.send(line)
            else:
                dataTamp = True
        elif cmd_extr == "quit":
            if data_split[3] == cmd_hex_disct["quit"]:
                con.send("<cmd-confirm-user-quit>")
                con.shutdown(s.SHUT_RD)
                con.close()
            else:
                dataTamp = True
        else:
            con.send("<cmd-server-"+getServerTime()+"-"+getHash(errorList["InvalidCommandError"])+"-"+errorList["InvalidCommandError"]+">")

        if dataTamp == True:
            print "[" + data_split[2] + "] "+data_split[4][:-1]+": Data tampering detected. The command " + prefix + cmd_extr + " is not going to be executed"
            con.send("error")

    elif data_split[0][1:] == "msg":
        content = data[data.index(data_split[3]) + len(data_split[3]) + 1:][:-1]
        hashCheckMsg = hashlib.sha224(content).hexdigest()
        if hashCheckMsg == data_split[3]:
            for singleClient in currentConnections:
                singleClient.send(data)
        else:
            lineMsgError = "<msg-server-"+getServerTime()+"-"+getHash(errorList["TamperError"])+"-"+errorList["TamperError"]+">"
            print "["+data_split[2]+"] Tamper Error: "+data_split[1]+" -> \nOriginal hash: "+data_split[3]+" \nTampered hash: " + hashCheckMsg
            con.send(lineMsgError)

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