import socket
import threading
from time import gmtime, strftime
import time
import hashlib
import sys

HOST = "127.0.0.1"
PORT = 50007

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

prefix = "!" # Prefix definition, used throughout the program to indicate that a command is being called
username = "" # Global variable that stores the username of the client (empty by default, will be set when the client joins the server)
thread2Closed = False # Global variable that checks if t2 has join back to parent thread

# Returns the current client time
def getClientTime():
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
    "addadmin": getHash("addadmin"),
    "removeadmin": getHash("removeadmin"),
    "servertitle": getHash("servertitle"),
    "clearbuffer": getHash("clearbuffer"),
    "kickuser": getHash("kickuser")
}

# A function that will run to set up the user before it can send and receive regular messages
def setupUser(socket):
    global username # Access the global username variable
    nameDone = False # Variable used to check that the user has chosen a unique username

    while nameDone == False: # Loop until we get a unique username from the user
        username = raw_input("Enter a username: ") # Prompt the user to input a username
        userHash = getHash(str(username))
        socket.sendall("<cmd-startup-namechange-"+userHash+"-"+str(username)+">") # Send starting data to the server, to set up the username

        data = socket.recv(1024) # Wait for a resposne from the server

        if "<cmd-confirm-true" in data: # If the username has been accepted
            print "Username has been set to: " + username # Print progress message to the console
            cmd_split = data.split('-') # Split the data that was received
            print "Welcome to the chat: " + cmd_split[3][0:-1] # Print a welcome message
            nameDone = True # Change the check variable to True, to show that the username has been set
            socket.sendall("<cmd-getbuffer-"+getClientTime()+"-"+getHash("getbuffer")+"-"+username+">") # Request the buffer from the server
        else: # If the username was declined, try again
            print "Error setting username. Try again..."

# Used to get input from the user
def readInput(user, socket):
    global cmd_hex_disct # Access the global hash dictionary
    global username
    while 1: # Loop indefinitely
        if thread2Closed == True:
            break
        text = raw_input() # Prompt the user for input  
        if prefix+"help" in text: # Check if the prefix + 'help' command is present in the input
            line = "<cmd-help-"+getClientTime()+"-"+cmd_hex_disct["help"]+"-"+username+">" # Build appropriate string
        elif prefix+"usercount" in text: # Check if the prefix + 'usercount' command is present in the input
            line = "<cmd-usercount-"+getClientTime()+"-"+cmd_hex_disct["usercount"]+"-"+username+">" # Build appropriate string
        elif prefix+"servertime" in text: # Check if the prefix + 'servertime' command is present in the input
            line = "<cmd-servertime-"+getClientTime()+"-"+cmd_hex_disct["servertime"]+"-"+username+">" # Build appropriate string
        elif prefix+"ping" in text: # Check if the prefix + 'ping' command is present in the input
            millis = int(round(time.time() * 1000)) # Get the current time in milliseconds, will be used to calculate the time taken
            line = "<cmd-ping-"+str(millis)+"-"+getHash(str(millis))+"-"+username+">" # Build appropriate string
        elif prefix+"quit" in text: # Check if the prefix + 'quit' command is present in the input
            line = "<cmd-quit-"+getClientTime()+"-"+cmd_hex_disct["quit"]+"-"+username+">" # Build appropriate string
        elif prefix+"serverquit" in text: # Check if the prefix + 'serverquit' command is present in the input
            line = "<cmd-serverquit-"+getClientTime()+"-"+cmd_hex_disct["serverquit"]+"-"+username+">" # Build appropriate string
        elif prefix+"changetitle" in text: # Check if the prefix + 'changetitle' command is present in the input
            newTitle = text[text.index(prefix+"changetitle") + len(prefix+"changetitle") + 1:] # Extract the new title parameter (everything after the command)
            if len(newTitle) == 0: # Check if the length is 0, which would make it invalid
                print("["+getClientTime()+"] server: The title cannot be empty. Try again.") # Inform the user
                line = "error" # Data to be sent to the server, will be ignored as it's not a valid data block that the server requires
            else: # not empty, proceed
                line = "<cmd-changetitle-"+getClientTime()+"-"+cmd_hex_disct["changetitle"]+"-"+username+"-"+newTitle+">" # Build the data block that will be sent to the server
        elif prefix+"addadmin" in text: # Check if the prefix + 'addadmin' command is present in the input
            newAdmin = text[text.index(prefix+"addadmin") + len(prefix+"addadmin") + 1:] # Extract the new admin parameter (everything after the command)
            line = "<cmd-addadmin-"+getClientTime()+"-"+cmd_hex_disct["addadmin"]+"-"+username+"-"+newAdmin+">" # Build the data block that will be sent to the server
        elif prefix+"removeadmin" in text: # Check if the prefix + 'removeadmin' command is present in the input
            toRemove = text[text.index(prefix+"removeadmin") + len(prefix+"removeadmin") + 1:] # Extract the admin name to remove parameter (everything after the command)
            line = "<cmd-removeadmin-"+getClientTime()+"-"+cmd_hex_disct["removeadmin"]+"-"+username+"-"+toRemove+">" # Build the data block that will be sent to the server
        elif prefix+"servertitle" in text: # Check if the prefix + 'servertitle' command is present in the input
            line = "<cmd-servertitle-"+getClientTime()+"-"+cmd_hex_disct["servertitle"]+"-"+username+">" # Build the data block that will be sent to the server
        elif prefix+"clearbuffer" in text: # Check if the prefix + 'clearbuffer' command is present in the input
            line = "<cmd-clearbuffer-"+getClientTime()+"-"+cmd_hex_disct["clearbuffer"]+"-"+username+">" # Build the data block that will be sent to the server
        elif prefix+"changename" in text: # Check if the prefix + 'changename' command is present in the input
            newName = text[text.index(prefix+"changename") + len(prefix+"changename") + 1:] # Extract the new name parameter (everything after the command)
            if len(newName) == 0: # Check if the length is 0, which would make it invalid
                print("["+getClientTime()+"] server: Your username cannot be empty. Try again.") # Inform the user
                line = "error" # Data to be sent to the server, will be ignored as it's not a valid data block that the server requires
            else:
                line = "<cmd-changename-"+getClientTime()+"-"+getHash(newName)+"-"+username+"-"+newName+">" # Build the data block that will be sent to the server
        elif prefix+"kickuser" in text:
            kickUser = text[text.index(prefix+"kickuser") + len(prefix+"kickuser") + 1:]
            line = "<cmd-kickuser-"+getClientTime()+"-"+cmd_hex_disct["kickuser"]+"-"+user+"-"+kickUser+">"
        else: # If no commands were detected, treat input as a regular message
            hashText = getHash(str(text)) # Hash the content that is going to be sent to the server
            line = "<msg-" + username + "-"+getClientTime()+"-" + hashText + "-" + text + ">" # Build appropriate string
        socket.sendall(line) # Send the string that was built above

# Used to read data coming in from the server
def readData(user, socket):
    global username
    while 1: # Loop indefinitely
        data = socket.recv(1024) # Store the received data in a variable
        #print(str(data))
        data_split = data.split('-') # Split the data variable
        try : # Attempt to extract the content of the message
            content = data[data.index(data_split[3]) + len(data_split[3]) + 1:][:-1] # Extract the content of the data (everything after the hash-)
            hashCheck = getHash(str(content)) # Get a hash using the content of the data

            if hashCheck == data_split[3]: # Check if the hash matches the provided hash
                if data_split[0][1:] == "cmd" and data_split[1] == prefix+"ping": # Check if the incoming data is a command, and specifically if it is the prefix + 'ping' command
                    millis = float(round(time.time() * 1000)) # Get the current time in milliseconds
                    timediff = millis - float(data_split[2]) # Calculate the difference between the current time and the time when the command was issued
                    print("PONG!!! The ping took "+str(int(timediff))+" millisecond(s)") # Print out to the user
                elif data_split[4][:-1] == "User Quitting": # Check if the message section matches after validated with hash
                    print "["+data_split[2]+"] " + data_split[1] + ": " + content # Print it out to the user
                    break
                elif data_split[4][:-1] == "Server Quitting": # Check if the message section matches after validated with hash
                    print "["+data_split[2]+"] " + data_split[1] + ": " + content # Print it out to the user
                    break
                elif data_split[0][1:] == "cmd" and data_split[1] == prefix+"changename": # Check if the data received is confirmation for a username change
                    username = content # Set the clients username to the username confirmed by the server
                elif data_split[4][:-1] == "User Kicked": # Check if the message section matches after validated with hash
                    print "["+data_split[2]+"] " + data_split[1] + ": " + content # Print it out to the user
                elif data_split[4][:-1] == "You have been kicked from the chat": # Check if the message section matches after validated with hash
                    print "["+data_split[2]+"] " + data_split[1] + ": " + content # Print it out to the user
                    break
                else: # Otherwise, it is a regular message
                    print "["+data_split[2]+"] " + data_split[1] + ": " + content # Print it out to the user
            else: # Otherwise message has been tampered with, print out an error
                print "Error processing your request. Please try again."
        except Exception as e: # If an error has occured
            print "Error processing your request. Please try again." # Inform the user

# Start the user setup process before any messages can be sent or received
setupUser(s)

# Create and start the thread to read input from the user
t1 = threading.Thread(target=readInput, args=(username, s))
t1.start()

# Create and start the thread to receive data from the server
t2 = threading.Thread(target=readData, args=(username, s))
t2.start()

t2.join() # Join the threads back to the parent thread
thread2Closed = True # Set the boolean to true to break t1's while loop
t1.join() # Join the threads back to the parent thread

# Shutdown and close the socket
s.shutdown(socket.SHUT_RDWR)
s.close()

sys.exit("Thank you for joining~ :D") # Exit the whole program when ends or in case of error occur