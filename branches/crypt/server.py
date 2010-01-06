import socket, thread, sys, os, time, string, pickle
from messageboard import postmessage, countmessages, listmessages, readmessage, delmessage
from namekeeper import registernick, freenick, changenick, nickregistered, nicklist
from rsa import *

global outmessagetext, outmessageid, pubkey, privkey

#load keys, generate pair if none exist
try:
    os.listdir('.').index('skey')
    os.listdir('skey')
    privkey = pickle.load(open('skey/private.bin', 'r'))
    pubkey = pickle.load(open('skey/public.bin', 'r'))
except (IOError, ValueError):
    print "Generating keypair, this will take several minutes..."
    pubkey, privkey = gen_pubpriv_keys(2048)
    print "Done, saving to files."
    os.mkdir('skey')
    pickle.dump(privkey, open('skey/private.bin', 'w'))
    pickle.dump(pubkey, open('skey/public.bin', 'w'))

port = 59387
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', port))
sock.listen(5) #listen for up to 5 new incoming requests at the same moment

outmessagetext = ''
outmessageid = -1
def sendmessage(text, nick):
    global outmessagetext, outmessageid
    if not nickregistered(nick) and nick != "tehsrvr":
        thread.exit_thread()
    if not (text.startswith('!') and nick == 'tehsrvr'): #no timestamp on server commands
        stamp = time.localtime()
        asciistamp = "%d:%d" % (stamp.tm_hour, stamp.tm_min)
        if stamp.tm_min < 10: asciistamp = string.replace(asciistamp, ':', ':0')
        text = asciistamp + " " + text
    print "BCAST: " + text
    outmessagetext = text
    outmessageid = outmessageid + 1

def sendloop(c, nick, ckey):
    global outmessagetext, outmessageid
    lastmessageid = outmessageid
    while 1:
        if outmessageid != lastmessageid:
            try:
                c.send(encrypt(outmessagetext, ckey))
            except: #the client is no longer available
                return
            lastmessageid = outmessageid
        else:
            time.sleep(0.01)

def getnick(c):
    nick = c.recv(1024)
    if len(nick) > 10:
        nick = nick[:9]
        c.send("!NOTE Nickname truncated to %s" % nick)
    return nick

def getkey(c):
    global pubkey
    print "!SENDKEY"+pickle.dumps(pubkey)
    c.send("!SENDKEY"+pickle.dumps(pubkey))
    rawkey = c.recv(2048)
    key = pickle.loads(rawkey)
    return key

def welcome(c):
    time.sleep(0.1)
    c.send('!NOTE Current users are: ' + string.join(nicklist(), ', '))
    messages = countmessages()
    if messages:
        c.send('!NOTE There are %d saved messages!!!' % messages)

def clientthread(c, ip):
    global privkey
    try:
        nick = getnick(c)
    except:
        print '%s getnick failed: %s' % (ip, str(sys.exc_info()[1]))
        return
    if registernick(nick) > 0: #if the nick is used
        c.send("!NOTE Nickname not valid.")
        c.send("!TERMINATE")
        c.close()
        return
    try:
        ckey = getkey(c)
    except:
        print '%s getkey failed: %s' % (nick, str(sys.exc_info()[1]))
        return
    print "%s logged in as %s" % (ip, nick)
    sendmessage("%s joined!" % nick, 'tehsrvr')
    c.send("!CHATMODE")
    thread.start_new_thread(sendloop, (c, nick, ckey))
    welcome(c)
    while 1: #recv loop. spends most of time on c.recv()
        try:
            message = c.recv(1024)
            if len(message) == 0: #client should not send empty messages
                raise IOError, "Client exit."
        except:
            sendmessage("%s quit: %s" % (nick, str(sys.exc_info()[1])), "tehsrvr")
            freenick(nick)
            break
        message = decrypt(message[1:], privkey)
        if message.startswith("/me "):
            message = string.replace(message, "/me ", "")
            sendmessage(" * %s %s" % (nick,message), nick)
        elif message == '/list':
            c.send('!NOTE Current users: ' + string.join(nicklist(), ', '))
        elif message.startswith('/nick '):
            oldnick = nick
            nick = string.split(message)[1]
            changenick(oldnick, nick)
            sendmessage(' The user %s is now known as %s' % (oldnick, nick), 'tehsrvr')
        elif message == '/exit':
            c.send('!TERMINATE')
        #messageboard commands
        elif message == '/msglist':
            c.send('!NOTE Messages: '+listmessages())
        elif message.startswith('/msgpost '):
            try:
                wordlist = string.split(message)
                title = wordlist[1]
                text = string.join(wordlist[2:])
            except:
                c.send('!NOTE Error parsing request: '+str(sys.exc_info()[1])+'\nYou might want to report this to the server operator.')
                continue
            c.send("!NOTE "+postmessage(title, text))
        elif message.startswith('/msgread '):
            try:
                title = string.split(message)[1]
            except IndexError:
                c.send('!NOTE Missing argument!')
                continue
            c.send("!NOTE "+readmessage(title))
        elif message.startswith('/msgdel '):
            try:
                title = string.split(message)[1]
            except IndexError:
                c.send('!NOTE Missing argument!')
                continue
            c.send("!NOTE "+delmessage(title))
        else:
            sendmessage("<%s> %s" % (nick, message), nick)

def main():
    print "Accepting clients from port %d" % port
    while 1:
        c, info = sock.accept()
        print "Connection request from %s." % info[0]
        thread.start_new_thread(clientthread, (c, info[0]))

try:
    main()
except:
    sock.close()
    sendmessage("Server exit, disconnecting all clients...", 'tehsrvr')
    time.sleep(1)
    sendmessage("!TERMINATE", 'tehsrvr')
    time.sleep(2)
    print sys.exc_info()

