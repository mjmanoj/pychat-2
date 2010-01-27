import socket, sys, time, string, ssl
from clienthandler import client
from config import serverconf
global config
config = serverconf()

clientlist = []
port = 59387
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', port))
sock.listen(5) #listen for up to 5 new incoming requests at the same moment

outmessagetext = ''
outmessageid = -1

def timestamp(text):
    stamp = time.localtime()
    asciistamp = "%d:%d" % (stamp.tm_hour, stamp.tm_min)
    if stamp.tm_min < 10: asciistamp = string.replace(asciistamp, ':', ':0')
    text = asciistamp + " " + text
    return text

def clientsend(client, text):
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

