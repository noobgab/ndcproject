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

cmd_hex_disct = {
    "help": hashlib.sha224("help").hexdigest(),
    "usercount": hashlib.sha224("usercount").hexdigest(),
    "servertime": hashlib.sha224("servertime").hexdigest(),
    "ping": hashlib.sha224("ping").hexdigest(),
    "quit": hashlib.sha224("quit").hexdigest()
}

def getClientTime():
    return strftime("%H:%M:%S", gmtime())

def getHash(str):
    return hashlib.sha224(str).hexdigest()

def setupUser(socket):
    global username
    nameDone = False

    while nameDone == False:
        username = raw_input("Enter a username: ")
        userHash = hashlib.sha224(str(username)).hexdigest()
        socket.sendall("<cmd-startup-namechange-"+userHash+"-"+str(username)+">")

        data = socket.recv(1024)

        if "<cmd-confirm-true" in data:
            print "Username has been set to: " + username
            cmd_split = data.split('-')
            print "Welcome to the chat: " + cmd_split[3][0:-1]
            nameDone = True
            socket.sendall("<cmd-getbuffer-"+getClientTime()+"-"+getHash("getbuffer")+"-"+username+">");
        else:
            print "Error setting username. Try again..."

def readInput(user, socket):
    global cmd_hex_disct
    while 1:
        text = raw_input()  
        if prefix+"help" in text:
            line = "<cmd-help-"+strftime("%H:%M:%S", gmtime())+"-"+cmd_hex_disct["help"]+"-"+user+">"
        elif prefix+"usercount" in text:
            line = "<cmd-usercount-"+strftime("%H:%M:%S", gmtime())+"-"+cmd_hex_disct["usercount"]+"-"+user+">"
        elif prefix+"servertime" in text:
            line = "<cmd-servertime-"+strftime("%H:%M:%S", gmtime())+"-"+cmd_hex_disct["servertime"]+"-"+user+">"
        elif prefix+"ping" in text:
            millis = int(round(time.time() * 1000))
            line = "<cmd-ping-"+str(millis)+"-"+getHash(str(millis))+"-"+user+">"
        elif prefix+"quit" in text:
            line = "<cmd-quit-"+strftime("%H:%M:%S", gmtime())+"-"+cmd_hex_disct["quit"]+"-"+user+">"
        else:
            hashText = hashlib.sha224(str(text)).hexdigest()
            line = "<msg-" + user + "-"+strftime("%H:%M:%S", gmtime())+"-" + hashText + "-" + text + ">"
        socket.sendall(line)
#<type-author-timestamp-hash-content>
def readData(user, socket):
    while 1:
        data = socket.recv(1024)
        data_split = data.split('-')
        try :
            content = data[data.index(data_split[3]) + len(data_split[3]) + 1:][:-1]
            hashCheck = hashlib.sha224(str(content)).hexdigest()

            if hashCheck == data_split[3]:
                if data_split[0][1:] == "cmd" and data_split[1] == prefix+"ping":
                    millis = float(round(time.time() * 1000))
                    timediff = millis - float(data_split[2])
                    print("PONG!!! The ping took "+str(int(timediff))+" millisecond(s)")
                else:
                    print "["+data_split[2]+"] " + data_split[1] + ": " + content
            else:
                print "Error processing your request. Please try again."
        except Exception as e:
            print "Error processing your request. Please try again."
            
setupUser(s)

t = threading.Thread(target=readInput, args=(username, s))
t.start()

t = threading.Thread(target=readData, args=(username, s))
t.start()
