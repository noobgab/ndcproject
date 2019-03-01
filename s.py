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
buffer = [] # Stores the messages that have been sent in the char room, then sent to new users that join
bufferTimes = [] # Keeps track of the post times of each message in the buffer
bufferTimeoutSeconds = 600 # Time in seconds, 600 = 10 minutes, 3600 = 1 hour, before a message is removed from the buffer
prefix = "!" # Prefix definition, used throughout the program to indicate that a command is being called
serverTitle = "No title" # Title of the server, changeable by admins
serverClose = False # Checks if the server is still online
userClose = False # Checks if the user is still online

# Global Lists
currentConnections = list() # stores the connections for all connected users
userList = list() # stores the usernames for all connected users
adminList = list() # stores a list of admins
adminList.append("admin") # add a default admin username into the list
commandList = ["help", "usercount", "servertime", "ping", "quit", "serverquit", "changetitle", "addadmin"] # keep a list of commands, will be sent to users

# Error messages used in the server. Stored in a dictionary so we can change it here, not in the middle of code
errorList = {
    "TamperError": "Server had trouble receiving your message. Please try again.",
    "InvalidCommandError": "This command does not exist, please type !help to get the list of available commands.",
    "AuthorizationError": "You do not have permission to perform this command.",
    "UnavailableUserError": "This user does not exist, please check the name you provided."
}

# Returns the current server time
def getServerTime():
    return strftime("%H:%M:%S", gmtime())

# Returns the hash of a given string
def getHash(str):
    return hashlib.sha224(str).hexdigest()

# Store the hashes of the most common commands, so we dont have to keep hashing them every time its called
cmd_hex_disct = {
    "help": getHash("help"),
    "usercount": getHash("usercount"),
    "servertime": getHash("servertime"),
    "ping": getHash("ping"),
    "quit": getHash("quit"),
    "serverquit": getHash("serverquit"),
    "changetitle": getHash("changetitle"),
    "addadmin": getHash("addadmin")
}

# Parses the input data that has come in from the user
def parseInput(data, con):
    global buffer # Access the global buffer list
    global bufferTimes # Access the global bufferTimes list
    global cmd_hex_disct # Access the global hash disctionary
    global serverClose # Access the global serverClose boolean variable
    global userClose # Access the global userClose boolean variable
    global currentConnections # Access the global list of client socket connections
    global serverTitle
    global userList
    global adminList

    print str(data) # Print out the data that has been received from the user
    data_split = data.split('-') # Split up the data to extract the information
    if data_split[0][1:] == "cmd": # Check if the data is a command, shown by "cmd"
        cmd_extr = data_split[1] # Extract the actual command received
        dataTamp = False # Variable used to check if the data received has been tampered with
        if cmd_extr == "help": # If the command that was extracted was "help"
            if data_split[3] == cmd_hex_disct["help"]: # Check if the hash provided matches the hash that we expected to see
                lineStr = "Here is a list of available commands: " # Build the return string
                for cmd in commandList:
                    lineStr += prefix + cmd + ", "
                lineStr = lineStr[0:-2] # Get rid of the ", " characters at the end

                line = "<cmd-server-"+getServerTime()+"-"+getHash(lineStr)+"-"+lineStr+">" # build the string
                con.send(line) # send the string built above to the user
            else: # The hashes didnt match, data corrupted, dont execute the command
                dataTamp = True
        elif cmd_extr == "usercount": # If the command that was extracted was "usercount"
            if data_split[3] == cmd_hex_disct["usercount"]: # Check if the hash provided matches the hash that we expected to see
                lineStr = "There are "+str(len(userList))+" user(s) online"
                line = "<cmd-server-"+getServerTime()+"-"+getHash(lineStr)+"-"+lineStr+">" # build the string
                con.send(line) # send the string built above to the user
            else: # The hashes didnt match, data corrupted, dont execute the command
                dataTamp = True
        elif cmd_extr == "servertime":  # If the command that was extracted was "servertime"
            if data_split[3] == cmd_hex_disct["servertime"]: # Check if the hash provided matches the hash that we expected to see
                lineStr = "The current server time is: " + getServerTime()
                line = "<cmd-server-"+getServerTime()+"-"+getHash(lineStr)+"-"+lineStr+">" # build the string
                con.send(line) # send the string built above to the user
            else: # The hashes didnt match, data corrupted, dont execute the command
                dataTamp = True
        elif cmd_extr == "ping": # If the command that was extracted was "ping"
            if data_split[3] == getHash(data_split[2]):
                #time.sleep(1) #uncomment this code to test the functionality of the ping command
                line = "<cmd-"+prefix+"ping-"+data_split[2]+"-"+getHash(data_split[2])+"-"+data_split[2]+">" # build the string
                con.send(line) # send the string built above to the user
            else: # The hashes didnt match, data corrupted, dont execute the command
                dataTamp = True
        elif cmd_extr == "quit": # If the command that was extracted was "quit"
            if data_split[3] == cmd_hex_disct["quit"]: # Check if the hash provided matches the hash that we expected to see
                lineStr = "User Quitting"
                line = "<cmd-server-"+getServerTime()+"-"+getHash(lineStr)+"-"+lineStr+">" # build the string
                con.send(line) # send the string built above to the user
                for oneCon in currentConnections:
                    print "Before: "+str(oneCon) # Debug 1: Shows the list of client connections before user quitting #
                currentConnections.remove(con) # Remove the conenction from the connections list
                for oneCon2 in currentConnections:
                    print "After: "+str(oneCon2) # Debug 2: Shows the list of client connections after user quitting #
                userClose = True # set userClose boolean variable to True to indicate disconnection of user
                userList.remove(data_split[4][:-1])
            else: # The hashes didnt match, data corrupted, dont execute the command
                dataTamp = True
        elif cmd_extr == "serverquit": # If the command that was extracted was "serverquit"
            if data_split[3] == cmd_hex_disct["serverquit"]: # Check if the hash provided matches the hash that we expected to see
                lineStr = "Server Quitting"
                line = "<cmd-server-"+getServerTime()+"-"+getHash(lineStr)+"-"+lineStr+">" # build the string
                for singleClient in currentConnections:
                    singleClient.send(line)
                serverClose = True # set serverClose boolean variable to True to indicate closing of server
        elif cmd_extr == "getbuffer": # If the command that was extracted was "getbuffer", only called once per user when they join (not actually callable by user afterwards)
            if data_split[3] == getHash("getbuffer"): # Check if the hash provided matches the hash that we expected to see
                for b in buffer: # Loop through the buffered messages
                    con.send(b) # Send them to the client one by one
                    time.sleep(0.001) # Sleep for a tiny amount to prevent overfloowing of messages which cause errors
        elif cmd_extr == "changetitle":
            if data_split[3] == cmd_hex_disct["changetitle"]:
                try: # Attempt to find the index position of the provided username, if it succeeds then the username is already taken
                    adminList.index(data_split[4])
                    serverTitle = data[data.index(data_split[4]) + len(data_split[4]) + 1:][:-1]
                    line = "The server title has changed to: " + serverTitle
                    lineStr = "<cmd-server-"+getServerTime()+"-"+getHash(line)+"-"+line+">"
                    for singleClient in currentConnections:
                        singleClient.send(lineStr)
                    # Proceed
                except ValueError as ve: # If the name is not in the list, it will throw an Exception
                    # User is not an admin
                    con.send("<cmd-server-"+getServerTime()+"-"+getHash(errorList["AuthorizationError"])+"-"+errorList["AuthorizationError"]+">")
            else:
                dataTamp = True
        elif cmd_extr == "addadmin":
            if data_split[3] == cmd_hex_disct["addadmin"]:
                try:
                    adminList.index(data_split[4])
                    try:
                        newAdminName = data[int(data.index(data_split[3])) + int(len(data_split[3]) + int(len(data_split[4])) + 2):][:-1]
                        userList.index(newAdminName)
                        adminList.append(newAdminName)
                        line = newAdminName + " has been promoted to admin"
                        lineStr = "<cmd-server-"+getServerTime()+"-"+getHash(line)+"-"+line+">"
                        for singleClient in currentConnections:
                            singleClient.send(lineStr)
                    except ValueError as ve:
                        con.send("<cmd-server-"+getServerTime()+"-"+getHash(errorList["UnavailableUserError"])+"-"+errorList["UnavailableUserError"]+">")
                except ValueError as ve:
                    con.send("<cmd-server-"+getServerTime()+"-"+getHash(errorList["AuthorizationError"])+"-"+errorList["AuthorizationError"]+">")
            else:
                dataTamp = True
        else: # Else none of the valid commands matched the provided command, let the user know
            con.send("<cmd-server-"+getServerTime()+"-"+getHash(errorList["InvalidCommandError"])+"-"+errorList["InvalidCommandError"]+">") # build the string, send it to user

        if dataTamp == True: # Check if the data tampering variable has been set to True, print out to console
            print "[" + data_split[2] + "] "+data_split[4][:-1]+": Data tampering detected. The command " + prefix + cmd_extr + " is not going to be executed"
            con.send("error") # Send a single word "error" to user, this will throw an error on their end as it does not amtch the protocol data

    elif data_split[0][1:] == "msg": # Check if the data is a message, shown by "msg"
        content = data[data.index(data_split[3]) + len(data_split[3]) + 1:][:-1] # Extract the content of the message (everything after the hash-. This allows the user to type "-" characters in their messages without breaking the server)
        hashCheckMsg = getHash(content) # Get the hash of the content
        if hashCheckMsg == data_split[3]: # Check if the hash provided matches the hash that we got using the content
            buffer.append(data)
            bufferTimes.append(int(round(time.time() * 1000)))
            for singleClient in currentConnections:
                singleClient.send(data)
        else: # The hashes didn't match, print a message to the console and let the user know
            lineMsgError = "<msg-server-"+getServerTime()+"-"+getHash(errorList["TamperError"])+"-"+errorList["TamperError"]+">" # Build the string to be sent to the user
            print "["+data_split[2]+"] Tamper Error: "+data_split[1]+" -> \nOriginal hash: "+data_split[3]+" \nTampered hash: " + hashCheckMsg # Print a message to the console
            con.send(lineMsgError) # Send the string that was built to the user

# Manages the connections between the clients and the server
def manageConnection(con, addr):
    global currentConnections # Access the global connections list
    global serverTitle # Access the global server title variable
    global userList # Access the global user list

    hashTextCmd = "" # Used for checking the username hashes

    print "Connected by: " + str(addr) # Print to the console

    nameDone = False # Variable used to check that the user has chosen a unique username
    while nameDone == False: # Loop until we get a unique username from the user
        data = con.recv(1024) # Receive the data - Done before any messages can be sent by the user
        checkstr = data.split("-") # Split the data
        print "Checking username: \"" + str(checkstr[4][0:-1]) + "\"" # Print progress message to console
        if checkstr[0] == "<cmd" and checkstr[2] == "namechange": # Check if a valid command has been sent
            usr = checkstr[4][0:-1] # Extract the username from the data
            if checkstr[3] == getHash(usr) and usr is not "": # Check if the extracted username matches the provided hash
                try: # Attempt to find the index position of the provided username, if it succeeds then the username is already taken
                    userList.index(usr)
                    print "Username declined" # Print to console
                    con.send("<cmd-confirm-false>") # Send a failed command to the user, to try again
                except ValueError as ve: # If the name is not in the list, it will throw an Exception
                    currentConnections.append(con) # Add the conenction to the connections list
                    userList.append(usr) # Add the username to the user list
                    nameDone = True # Set the variable to True to show that the name has been set successfully
                    print "Username accepted" # Print a progress message to console
                    con.send("<cmd-confirm-true-"+serverTitle+">") # Send a success message to the user, to continue and let user send actual messages
                    hashTextCmd = getHash(usr+" has joined the chat") # Get a hash of the message
                    typeMsg = getServerTime() # Get the time data to be sent to users
                    for singleClient in currentConnections: # Loop through all the connections in the list
                        if singleClient == con: # If the current connection is the connection in the loop
                            time.sleep(0.001) # Pause the thread for a tiny ammount, to prevent overflooding the clients
                            typeMsg = "startup" # Print startup instead of a timestamp
                        
                        lineMsgJoin = "<msg-server-"+typeMsg+"-"+hashTextCmd+"-"+usr+" has joined the chat>" # Build the return string
                        singleClient.send(lineMsgJoin) # Return the string to the user
            else: # If any other errors occur, send a failing message for the user to try again
                con.send("<cmd-confirm-false>")

    while 1: # After the name has been set successfully, continue listening for messages from the client
        # Shutdown and close the client connection if both userClose is true and the connection is not in currentConnections list
        if userClose == True and con not in currentConnections:
            con.shutdown(socket.SHUT_RDWR)
            con.close()
            break
        data = con.recv(1024) # Receive the data from the user
        parseInput(data, con) # Send the data received to parseInput to deal with the data
        if serverClose == True:
            break
        print "Server Offline Status: "+str(serverClose)

# Processes the messages in the buffer, and removes old messages once they reach a certain amount of time
def bufferProcess():
    global bufferTimeoutSeconds # Access the global buffer message time out variable
    global bufferTimes # Access the global buffer times list
    global buffer # Access the global buffer list

    while 1: # Keep looping, always be ready to remove a message after it has reached its time limit
        cs = int(round(time.time() * 1000)) # Get the current timestamp
        for ts in bufferTimes: # Loop through all the stored timestamps in the global list
            if cs - ts > (bufferTimeoutSeconds*1000): # If the difference is greater than the provided allowed time
                index = bufferTimes.index(ts) # Get the index of the timestamp within the list
                del buffer[index] # Remove the actual message associated with this timestamp
                del bufferTimes[index] # Remove the timestamp form the list

bt = threading.Thread(target=bufferProcess, args=()) # Crate the bufferProcess thread
bt.start() # Start the bt thread

# Keep listening for incoming connections continuously
while 1:
    s.listen(1)
    con, addr = s.accept() # Accept a connection, storing the connection object and an address

    t = threading.Thread(target=manageConnection, args=(con, addr)) # Create a new thread for the user that has just joined
    t.start() # Start the new thread
    if serverClose == True:
        break

bt.join() # Join the bufferProcess threads back to the parent thread
t.join() # Join the threads back to the parent thread

# Shutdown and close the socket
s.shutdown(socket.SHUT_RDWR)
s.close()