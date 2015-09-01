New version of Pychat, TKinter is being used to create a GUI.

# Getting Started #
## Requirements ##
  * Python 2.x
  * An SVN client, such as TortiseSVN (for Windows)
  * A computer capable of running python
  * A clue about how to use chat programs

## Instructions ##
To use it, check out the source, run the server, and use on of the client scripts to connect to it. If you want to connect to a server running on a different computer, add a file called serverinfo.py to the directory that client.py is in with this line: `IP='123.45.67.89'` (more info about configuration below). Of course, change the ip to that of the computer you want to connect to. There are more directions below.

# Documentation #
More docs are available on request.

## Basic client user guide ##
### Commands ###
These are commands you can send to the server to get different results.

/exit:
simply quits... for those who like typing instead of clicking the quit button, or are using the non-GUI client.

/list:
displays a list of the nicknames of the clients in the room.

/me {text}:
posts a message in the form of " `*` nickname {text}". So, if I'm logged in as muddyclaw, and I say "/me dances", it will look like " `*` muddyclaw dances".

/nick {text}:
This command will change your current nickname to {text}.

There is also the ability to leave messages for users currently not connected. If there are any messages currently saved to a server, you will be notified when you connect to it. These are the commands relating to saved messages:

/msglist:
displays a list of the currently saved messages' titles.

/msgread {title}:
displays the content of the message with {title}.

/msgpost {title} {text}:
saves a message with the title set to {title} and the body set to {text}. Note that the title cannot have any spaces or characters not allowed in file names, and that the text of the message cannot be longer than 600 letters.

/msgdel {title}:
delete the saved message with the title of {title}.

### Configuration ###
The configuration file for the client is serverinfo.py. These are the options:
| Name | Default | Description |
|:-----|:--------|:------------|
| IP   | '127.0.0.1' | The IP of the server to connect to by default. |
| secure | False   | Use a [secure](http://en.wikipedia.org/wiki/Transport_Layer_Security) connection for all communications |
| configuredtoserve | False   | Whether the client has been set up to work as a TLS server. |
| certfile | 'cert.pem' | Location of the certificate. |

configuredtoserve should only be enabled if you have generated a certificate file as detailed in the server user guide, and want to be able to use it if needed. This is the "needed" situation: You want to connect to a server which does not have its own cert, but you still want to use encryption. In this case, you will need to generate a key and cert to use (as specified in the server user guide), enable this option, and point certfile to the key/certificate file. Note that if the server has a certfile set, it will be used whether this one is present or not. If you need help with this, ask Marcus.

This is an example configuration file:
```
IP='127.0.0.1' #connect to localhost
secure=False #do not use an encrypted connection
```

## Basic Server User Guide ##
Running a server is very easy, just run the server.py script. Running this will create a "messages" directory in the working directory of the script and will save messages posted using /msgpost here. It is safe to delete this directory, but you will lose all saved messages. Also, keep in mind that any user can delete saved messages.

If you want people to be able to connect to the server from outside your network using your external IP address, you will need to set up port forwarding on your router and make sure you firewall is set to allow incoming TCP connections for either python.exe and/or port 59387. Both of these topics are beyond the scope of this guide.

If you want to be able to use an encrypted connection, you need to generate and sign a key, if you don't already have one. The key can be self-signed, but it needs a certificate of some sort to keep the python ssl module happy. A key generated using the method [here](http://docs.python.org/dev/library/ssl.html#ssl-certificates) will work fine (except that you should add "-newkey rsa:2048" to the command for better security). You also need to do some configuration as defined in the next section.

### Configuration ###
The configuration file for the server is serverconf.py. These are the options:
| Name | Default | Description |
|:-----|:--------|:------------|
| hascert | False   | A cert file is present and usable. |
| forceencryption | False   | Use encryption for all connections. |
| certfile | 'cert.pem' | The location of your key/certificate file. |

certfile is where you have put your (possibly self-signed) pem-formatted and certified rsa private key file. There is more information on generating one of these above.

hascert should be enabled only if you have a certfile at the location specified in certfile. If you enable this and do not have a certfile, weird errors will occur when trying to secure a connection with a client.

This is an example serverconf.py:
```
forceencryption=False #do not use encryption unless the client asks to
certfile='myprivatekey.pem' #I put my key somewhere different than most people!!!
```

## Basic Developer Guide ##
### Developer Mode ###
Developer mode was designed to enable developers to run a "production" server while at the same experimenting with code changes with either the server or the client. This is harder than it sounds, both because running two servers on the same port is not possible, and because any clients run in normal mode will connect to the production server, which may not be desirable. In the server, developer mode changes the port to a different one, and makes it so that it will only accept connections from the computer it is running on. In the client, developer mode changes the port to the same one that the server changes to, and only connects to servers running on the same computer.

To enable devmode, add `devmode = True` to commonconf.py.
### Writing Client Backends ###
If you want to write a frontend for client.py, you need to provide a function for input, output, and exiting. Here are the specifications for those functions:
#### input ####
This function is what is used to send messages to the server. It needs to block until there is a message to send, and then return the message text. The function should also take a prompt as an optional argument. The prompt when waiting for a message to send is not provided. For example, the built-in raw\_input() function satisfies these requirements.
#### output ####
This function is used to output messages from the server and other notifications to the screen. It should not block and should take a single string as an argument. For example, the builtin print() function in python 2.6 and later satisfies these requirements.
#### exit ####
This function notifies the rest of the program that the client is exiting and will not be sending any more output or asking for any more input. This function may block, but the client will not completely exit until it returns. The program is not required to exit immediately, and may even make a new client thread.

To start a connection, define your input, output, and exit functions as e.g. printit(), gettext(), and leavenow(), and use this code:
```
import client
client.callbacks(printit, gettext, leavenow)
```
This function will block until the client exits, so you will probably want to start it as a different thread. Note that you can also pass a custom server IP as argument 4. If none is provided, the client will use the IP specified in serverinfo.py

An example frontend is tkclient.py.