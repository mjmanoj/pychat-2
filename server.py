import socket, sys, time
from clienthandler import client
from config import serverconf
global config
config = serverconf()

clientlist = []
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if not config.devmode:
    bindto = config.bind
    port = config.port
else:
    bindto = 'localhost'
    port = 59287
    print "Using dev mode, see googlecode documentation for more details!!!"
sock.bind((bindto, port))
sock.listen(5) #listen for up to 5 new incoming requests at the same moment

def timestamp(text = None):
    stamp = time.localtime()
    asciistamp = str(stamp.tm_hour)
    if stamp.tm_min < 10:   asciistamp += ':0' + str(stamp.tm_min)
    else:                   asciistamp += ':'+ str(stamp.tm_min)
    if stamp.tm_sec < 10:   asciistamp += ':0' + str(stamp.tm_sec)
    else:                   asciistamp += ':' + str(stamp.tm_sec)
    if text != None:
        text = asciistamp + " " + text
        return text
    else:
        return asciistamp

def clientsend(client, text):
    if not client.ready:
        return
    if client.send(text):
        clientlist.remove(client)

def sendmessage(text, nick):
    if not (text.startswith('!') and nick == 'tehsrvr'): #no timestamp on server commands
        text = timestamp(text)
    print "BCAST: " + text
    for client in clientlist:
        clientsend(client, text)

def sendto(nick, targetnick, text):
    text = "%s -> %s: %s" % (nick, targetnick, text)
    text = timestamp(text)
    success = 0
    for client in clientlist:
        if client.nick == targetnick:
            clientsend(client, text)
            success = 1
    if success:
        if nick != targetnick:
            for client in clientlist:
                if client.nick == nick: #also send a copy to the sender
                    clientsend(client, text)
        print "MCAST: " + text
        return 0
    else:
        return 1

def main():
    print "Accepting clients from port %d" % port
    while 1:
        c, info = sock.accept()
        print timestamp("Handling connection request from %s." % info[0])
        clientlist.append(client(c, info[0], sendmessage, sendto, config))

try:
    main()
except:
    sock.close()
    sendmessage("Server exit, disconnecting all clients...", 'tehsrvr')
    time.sleep(1)
    sendmessage("!TERMINATE", 'tehsrvr')
    time.sleep(2)
    print sys.exc_info()

