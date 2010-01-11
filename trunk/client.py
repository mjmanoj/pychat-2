import socket, thread, string, sys, time

#load settings
try:
    #if you want to use a server other than localhost, add a file
    #named serverinfo.py in the same directory as this file with
    #one line: IP = '12.34.56.789' #change to the desired ip...
    from serverinfo import IP
except:
    #if there is no serverinfo.py file, just use localhost
    IP = 'localhost'

try:
    #you can also set whether or not to use a secure connection
    from serverinfo import secure
except:
    secure = False

global buffertext, bufferfull
bufferfull = 0
buffertext = ''

global socketclosed
socketclosed = 0

class clientsock():
    global socketclosed
    def __init__(self, server, infoout):
        self.infoout = infoout
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(server)
        self.closed = False
        self.secured = False

    def send(self, text):
        if type(text) != type('string'):
            raise TypeError, 'send() needs a string.'
        if self.closed:
            raise NameError, 'Socket has been closed.'
        try:
            self.s.send(text)
        except:
            self.close()

    def recv(self):
        if self.closed:
            raise NameError, 'Socket has been closed.'
        try:
            data = self.s.recv(1024)
            if len(data) == 0:
                raise ValueError, 'Empty packet.'
            return data
        except:
            self.close()

    def secure(self): #converts self.s to a secure TLS socket if possible
        if self.secured:
            raise ValueError, "Socket already secure."
        try:
            import ssl
        except:
            raise ImportError, "SSL not supported by python installation."
        if self.recv() != 'go':
            raise IOError, "Pre-wrapping sanity check failed."
        self.send('now')
        self.s = ssl.wrap_socket(self.s, ssl_version=ssl.PROTOCOL_TLSv1)
        if self.recv() != 'it works?':
            raise IOError, "Post-wrapping sanity check failed."
        self.send('heard you!')
        if self.recv() != 'completed with success.':
            raise IOError, "Final sanity check failed."
        return

    def close(self, reason = ''):
        if self.closed:
            self.infoout("clientsock object closed twice. Report this message.")
            return
        self.s.close()
        self.closed = True
        self.infoout("Socket closed.")

def inputthread(infunc, s):
    while 1:
        message = infunc()
        if len(message) == 0:
            continue
        s.send(message)

def netmanager(s, outfunc, infunc, killfunc):
    while 1:
        command = s.recv()
        if not command.startswith("!"):
            outfunc(command)
        elif command.startswith("!CHATMODE"):
            outfunc("Nickname accepted, entering chat mode.")
            thread.start_new_thread(inputthread, tuple([infunc, s]))
        elif command.startswith("!NOTE"):
            outfunc(string.replace(command, "!NOTE ", "Server: "))
        elif command.startswith("!TERMINATE"):
            outfunc("Client terminated.")
            s.close()
            socketclosed = 1
            time.sleep(0.1)
            killfunc()
            return

def callbacks(outfunc, infunc, killfunc, server=IP, encrypted=secure):
    outfunc("Connecting...")
    try:
        s = clientsock((IP, 59387), outfunc)
    except:
        outfunc("Could not connect to server: " + str(sys.exc_info()[1]))
        killfunc()
    outfunc("Server found.")
    s.send(str(int(encrypted)))
    try:
        if int(s.recv()):
            outfunc("Securing connection...")
            s.secure()
            outfunc("Connection secure.")
        else:
            if encrypted:
                raise IOError, "Server is not able to handle a secure connection."
    except:
        if encrypted:
            print sys.exc_info()[1]
            outfunc("Connection could not be secured. Exiting.")
            killfunc()
            return
    nick = (infunc("Enter nickname: "))
    s.send(nick)
    netmanager(s, outfunc, infunc, killfunc)

def main():
    def printfunc(text): print text #print is not a function in 2.5 and earlier
    callbacks(printfunc, raw_input, exit)

if __name__ == '__main__':
    main()
