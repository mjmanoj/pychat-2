import socket, thread, sys, time, string

global outmessagetext, outmessageid, time

port = 59387
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', port))
sock.listen(5) #listen for up to 5 new incoming requests at the same moment

nicklist = []
def registernick(nick):
    collision = 0
    if nick == "tehsrvr":
        collision = 1 #that one is permenantly reserved
    for usedname in nicklist:
        if nick == usedname:
            collision = 1
    if collision:
        return 1
    else:
        nicklist.append(nick)
        return 0

def freenick(nick):
    nicklist.remove(nick)
    return

def nickregistered(nick):
    collision = 0
    for usedname in nicklist:
        if nick == usedname:
            collision = 1
    return collision

def userlist():
    return nicklist

outmessagetext = ''
outmessageid = -1
def sendmessage(text, nick):
    global outmessagetext, outmessageid
    if not nickregistered(nick) and nick != "tehsrvr":
        thread.exit_thread()
    if not nick == 'tehsrvrnotnotnotnot': #no timestamp on server messages (disabled)
        stamp = time.localtime()
        asciistamp = "%d:%d" % (stamp.tm_hour, stamp.tm_min)
        if stamp.tm_min < 10: asciistamp = string.replace(asciistamp, ':', ':0')
        text = asciistamp + " " + text
    print "BCAST: " + text
    outmessagetext = text
    outmessageid = outmessageid + 1

def sendloop(c, nick):
    global outmessagetext, outmessageid
    lastmessageid = outmessageid
    while 1:
        if outmessageid != lastmessageid:
            try:
                c.send(outmessagetext)
            except:
                "ERROR IN SEND LOOP\n%s: %s" % (nick, sys.exc_info()[1])
            lastmessageid = outmessageid
        else:
            time.sleep(0.01)

def getnick(c):
    c.send("!SENDNICK")
    nick = c.recv(1024)
    if len(nick) > 10:
        nick = nick[:9]
        c.send("!NOTE Nickname truncated to %s" % nick)
    return nick

def clientthread(c, ip):
    try:
        nick = getnick(c)
    except:
        print '%s disappeared %s' % (ip, sys.exc_info()[1])
        return
    if registernick(nick) > 0: #if the nick is used
        c.send("!NOTE Nickname in use.")
        c.send("!TERMINATE")
        c.close()
        return
    print "%s is now known as %s" % (ip, nick)
    c.send("!CHATMODE")
    time.sleep(0.1)
    sendmessage("%s joined!" % nick, 'tehsrvr')
    thread.start_new_thread(sendloop, (c, nick))
    while 1: #recv loop. spends most of time on c.recv()
        try:
            message = c.recv(1000)
            if len(message) == 0: #client should not send empty messages
                raise IOError, "Client quit"
        except:
            sendmessage("%s quit: %s" % (nick, sys.exc_info()[1]), "tehsrvr")
            freenick(nick)
            break
        message = message.strip("\xaa")
        if message[:4] == "/me ":
            message = string.replace(message, "/me ", "")
            sendmessage(" * %s %s" % (nick,message), nick)
        elif message[:5] == '/list':
            c.send('!NOTE Current users: ' + string.join(userlist(), ', '))
        elif message[:5] == '/exit':
            c.send('!TERMINATE')
        else:
            sendmessage("<%s> %s" % (nick, message), nick)

        
def varmon():
    while 1:
        global outmessagetext, outmessageid
        print outmessagetext, outmessageid
        time.sleep(2)
#thread.start_new_thread(varmon, ())

def main():
    print "Accepting clients from port %d" % port
    while 1:
        c, info = sock.accept()
        print "Connection request from %s." % info[0]
        thread.start_new_thread(clientthread, (c, info[0]))

try:
    main()
except:
    sendmessage("!TERMINATE", 'tehsrvr')
    time.sleep(3)
    sock.close()
    print sys.exc_info()

