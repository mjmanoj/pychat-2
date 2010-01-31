from messageboard import postmessage, countmessages, listmessages, readmessage, delmessage
from namekeeper import registernick, freenick, changenick, nicklist
import thread, string, sys, time

class client():
    def __init__(self, c, ip, bcast, monocast, serverconf):
        global config
        config = serverconf
        self.c = c
        self.ip = ip
        self.bcast = bcast
        self.monocast = monocast
        self.closed = False
        self.nick = ip #temporary handle, until one is assigned.
        self.ready = False
        thread.start_new_thread(self.mainthread, tuple([]))

    def __del__(self):
        self.close()

    #connection handling functions
    def send(self, text):
        if self.closed: return
        try:
            self.c.send(text)
        except: #sending didn't work
            print "Client %s no longer available" % self.nick
            self.close()
            return 1

    def recv(self):
        if self.closed: return
        data = self.c.recv(4096)
        if len(data) == 0: #client should not send empty messages
            self.close()
            raise IOError, "Client quit (connection interrupted)."
        data = data.strip("\xaa")
        return data

    def secure(self, serving): #converts self.c into a secure TLS socket if possible
        import ssl
        self.c.send('go')
        if self.recv() != 'now':
            raise IOError, "Pre-wrapping sanity check failed."
        if serving:
            self.c = ssl.wrap_socket(self.c, server_side=True, certfile=config.certfile, ssl_version=ssl.PROTOCOL_TLSv1)
        else:
            self.c = ssl.wrap_socket(self.c, ssl_version=ssl.PROTOCOL_TLSv1)
        self.c.send('it works?')
        if self.recv() != 'heard you!':
            raise IOError, "Post-wrapping sanity check failed."
        self.c.send('completed with success.')
        return

    def close(self):
        if self.closed: return
        self.c.close()
        self.closed = True
        return

    #general functions
    def getnick(self):
        tmpnick = self.recv()
        if len(tmpnick) > 10:
            tmpnick = tmpnick[:9]
            self.send("!NOTE Nickname truncated to %s" % tmpnick)
        return tmpnick

    def welcome(self):
        time.sleep(0.1)
        self.send('!NOTE Current users are: ' + string.join(nicklist(), ', '))
        messages = countmessages()
        if messages:
            self.send('!NOTE There are %d saved messages!!!' % messages)

    #the "main" function
    def mainthread(self):
        try:
            clientprefs = self.recv()
            clientwantsencryption = int(clientprefs[0])
            clientcanserve = int(clientprefs[1])
            if config.sslavailable and (clientcanserve or config.canserve):
                #if the server can do any kind of encryption and either party can serve
                encryptionpossible = True
            else:
                encryptionpossible = False
            if encryptionpossible and (clientwantsencryption or
                                       config.forceencryption):
                usingencryption = True
            else:
                usingencryption = False
            if config.canserve:
                serving = True
            else:
                serving = False
            self.send(str(int(usingencryption)) + str(int(serving)))
            #if encryption is not possible even though it is required by the client, it will d/c at this point
            if encryptionpossible:
                self.secure(serving)
                print 'Using secure connection with %s (serving = %s)' % (self.ip, str(bool(serving)))
        except:
            print 'Securing connection with %s failed: %s' % (self.ip, str(sys.exc_info()[1]))
            self.send('oops!') #this will trigger sanity checks to fail at the client, rather than just a hang.
            return
        try:
            tmpnick = self.getnick()
        except:
            print '%s getnick failed: %s' % (self.ip, str(sys.exc_info()[1]))
            return
        if registernick(tmpnick) > 0: #if the nick cannot be registered
            self.send("!NOTE Nickname in use.")
            self.send("!TERMINATE")
            self.close()
            return
        else:
            self.nick = tmpnick
        print "%s logged in as %s" % (self.ip, self.nick)
        self.send("!CHATMODE")
        time.sleep(0.1)
        self.bcast("%s joined!" % self.nick, 'tehsrvr')
        self.welcome()
        self.ready = True
        while 1: #recv loop. spends most of time on self.recv()
            try:
                message = self.recv()
            except:
                self.bcast("%s quit: %s" % (self.nick, str(sys.exc_info()[1])), "tehsrvr")
                freenick(self.nick)
                break
            if message.startswith('/'):
                self.command(message)
            else: #just a regular message
                self.bcast("<%s> %s" % (self.nick, message), self.nick)

    def command(self, message): #handles command messages
        if message.startswith("/me "):
            message = string.replace(message, "/me ", "")
            self.bcast(" * %s %s" % (self.nick,message), self.nick)
        
        elif message == '/list':
            self.send('!NOTE Current users: ' + string.join(nicklist(), ', '))
        
        elif message.startswith('/to'):
            targetnick = string.split(message)[0][3:]
            text = string.join(string.split(message)[1:])
            if self.monocast(self.nick, targetnick, text):
                self.send('!NOTE Error sending PM.')
        
        elif message.startswith('/nick '):
            oldnick = self.nick
            newnick = string.split(message)[1]
            if changenick(oldnick, newnick) > 0: #if the nick is used
                self.send("!NOTE Nickname in use.")
                return
            self.nick = newnick
            self.bcast(' * The user %s is now known as %s' % (oldnick, self.nick), 'tehsrvr')
        
        elif message == '/exit':
            self.send('!TERMINATE')
        
        #messageboard commands
        elif message == '/msglist':
            self.send('!NOTE Messages: '+listmessages())
        elif message.startswith('/msgpost '):
            try:
                wordlist = string.split(message)
                title = wordlist[1]
                text = string.join(wordlist[2:])
            except:
                self.send('!NOTE Error parsing request: '+str(sys.exc_info()[1])+'\nYou might want to report this to the server operator.')
                return
            self.send("!NOTE "+postmessage(title, text))
        
        elif message.startswith('/msgread '):
            try:
                title = string.split(message)[1]
            except IndexError:
                self.send('!NOTE Missing argument!')
                return
            self.send("!NOTE "+readmessage(title))
        
        elif message.startswith('/msgdel '):
            try:
                title = string.split(message)[1]
            except IndexError:
                self.send('!NOTE Missing argument!')
                return
            self.send("!NOTE "+delmessage(title))
        
        else: #not a known command
            self.send("!NOTE Command not valid.")
