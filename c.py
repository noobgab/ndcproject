import socket
import threading
from time import gmtime, strftime
import time
import hashlib

HOST = "127.0.0.1"
PORT = 50007

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

prefix = "!" # Prefix definition, used throughout the program to indicate that a command is being called
username = "" # Global variable that stores the username of the client (empty by default, will be set when the client joins the server)

# Store the hashes of the most common commands, so we dont have to keep hashing them every time its called
cmd_hex_disct = {
    "help": hashlib.sha224("help").hexdigest(),
    "usercount": hashlib.sha224("usercount").hexdigest(),
    "servertime": hashlib.sha224("servertime").hexdigest(),
    "ping": hashlib.sha224("ping").hexdigest(),
    "quit": hashlib.sha224("quit").hexdigest()
}

# Returns the current client time
def getClientTime():
    return strftime("%H:%M:%S", gmtime())

# Returns the hash of a given string
def getHash(str):
    return hashlib.sha224(str).hexdigest()

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
            socket.sendall("<cmd-getbuffer-"+getClientTime()+"-"+getHash("getbuffer")+"-"+username+">"); # Request the buffer from the server
        else: # If the username was declined, try again
            print "Error setting username. Try again..."

# Used to get input from the user
def readInput(user, socket):
    global cmd_hex_disct # Access the global hash dictionary
    while 1: # Loop indefinitely
        text = raw_input() # Prompt the user for input  
        if prefix+"help" in text: # Check if the prefix + 'help' command is present in the input
            line = "<cmd-help-"+strftime("%H:%M:%S", gmtime())+"-"+cmd_hex_disct["help"]+"-"+user+">" # Build appropriate string
        elif prefix+"usercount" in text: # Check if the prefix + 'usercount' command is present in the input
            line = "<cmd-usercount-"+strftime("%H:%M:%S", gmtime())+"-"+cmd_hex_disct["usercount"]+"-"+user+">" # Build appropriate string
        elif prefix+"servertime" in text: # Check if the prefix + 'servertime' command is present in the input
            line = "<cmd-servertime-"+strftime("%H:%M:%S", gmtime())+"-"+cmd_hex_disct["servertime"]+"-"+user+">" # Build appropriate string
        elif prefix+"ping" in text: # Check if the prefix + 'ping' command is present in the input
            millis = int(round(time.time() * 1000)) # Get the current time in milliseconds, will be used to calculate the time taken
            line = "<cmd-ping-"+str(millis)+"-"+getHash(str(millis))+"-"+user+">" # Build appropriate string
        elif prefix+"quit" in text: # Check if the prefix + 'quit' command is present in the input
            line = "<cmd-quit-"+strftime("%H:%M:%S", gmtime())+"-"+cmd_hex_disct["quit"]+"-"+user+">" # Build appropriate string
        else: # If no commands were detected, treat input as a regular message
            hashText = getHash(str(text)) # Hash the content that is going to be sent to the server
            line = "<msg-" + user + "-"+strftime("%H:%M:%S", gmtime())+"-" + hashText + "-" + text + ">" # Build appropriate string
        socket.sendall(line) # Send the string that was built above

# Used to read data coming in from the server
def readData(user, socket):
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
                else: # Otherwise, it is a regular message
                    print "["+data_split[2]+"] " + data_split[1] + ": " + content # Print it out to the user
            else: # Otherwise message has been tampered with, print out an error
                print "Error processing your request. Please try again."
        except Exception as e: # If an error has occured
            print "Error processing your request. Please try again." # Inform the user

# Start the user setup process before any messages can be sent or received
setupUser(s)

# Create and start the thread to read input from the user
t = threading.Thread(target=readInput, args=(username, s))
t.start()

# Create and start the thread to receive data from the server
t = threading.Thread(target=readData, args=(username, s))
t.start()
