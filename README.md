# NDC Project

Project files for Network Distributed Computing - Assignment 1

# Group Members

- B00100126
- B00085922
- B00108141

# Commands

- <b>!help</b> : lists the available commands
- <b>!servertitle</b> : lists the current server title
- <b>!changename X</b> : allows the user to change their username, where X = new username
- <b>!usercount</b> : lists the number of users online
- <b>!servertime</b> : lists the current server time
- <b>!ping</b> : tests the connection between the client and the server, lists the amount of time the command process took
- <b>!quit</b> : allows the user to quit the chat server
- <b>!serverquit</b> : allows an admin to close the server
- <b>!clearbuffer</b> : allows an admin to clear the message buffer
- <b>!changetitle X</b> : allows an admin to change the title of the server, where X = new title
- <b>!addadmin X</b> : allows an admin to add another user to the admin list, where X = the username of to add
- <b>!removeadmin X</b> : allows an admin to remove another user from the admin list, where X = the username to remove
- <b>!kickuser X</b> : allows an admin to kick another user form the chat, where X = username to kick

# Update Log

#### 2/3/2019:
- kickuser command is fully operational

#### 1/3/2019:
- Finished client quit cmd :D
- Admin can now promote other users to be admins on the server
- Admin can now remove admin privileges from users
- Servertitle command now added, to show the current server title
- Clearbuffer command now added, the admin can clear the buffer (remove every message from the buffer)
- Changename command now added, users are able to change their usernames

#### 23/2/2019:
- Further improved quit command

#### 22/2/2019:
- Got most of the quit and serverquit command working
