import socket, thread, string, sys, time
from config import clientconf
global config
config = clientconf()

class clientsock():
    global config
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

    def secure(self, serving): #converts self.s to a secure TLS socket if possible
        if self.secured:
            raise ValueError, "Socket already secure."
        if not config.sslavailable:
            raise ImportError, "SSL not supported by python installation."
        else:
            import ssl
        if self.recv() != 'go':
            raise IOError, "Pre-wrapping sanity check failed."
        self.send('now')
        if serving:
            self.s = ssl.wrap_socket(self.s, server_side=True, certfile=config.certfile, ssl_version=ssl.PROTOCOL_TLSv1)
        else:
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
        if command == None:
            command = '!TERMINATE'
        if not command.startswith("!"):
            outfunc(command)
        elif command == "!CHATMODE":
            outfunc("Nickname accepted, entering chat mode.")
            thread.start_new_thread(inputthread, tuple([infunc, s]))
        elif command.startswith("!NOTE"):
            outfunc(string.replace(command, "!NOTE ", "Server: "))
        elif command == "!PING":
            s.send("/PONG")
        elif command == "!TERMINATE":
            outfunc("Client terminated.")
            if not s.closed:
                s.close()
            time.sleep(0.1)
            killfunc()
            return

def callbacks(outfunc, infunc, killfunc):
    if not config.devmode:
        server = config.IP
        port = config.port
    else:
        server = 'localhost'
        port = 59287
        outfunc("Using dev mode, see googlecode documentation for more details!!!")
    print(port)
    outfunc("Connecting...")
    try:
        s = clientsock((server, port), outfunc)
    except:
        outfunc("Could not connect to server: " + str(sys.exc_info()[1]))
        killfunc()
    outfunc("Server found.")
    s.send(str(int(config.secure)) + str(int(config.canserve)))
    cryptresults = s.recv()
    usingcrypt = int(cryptresults[0])
    serving = not int(cryptresults[1]) #client serving bool is inverse of corresponding server bool
    try:
        if usingcrypt:
            outfunc("Securing connection (requested by server: %s)..." % str(bool(usingcrypt and not config.secure)))
            if serving: outfunc("Serving SSL/TLS.")
            s.secure(serving)
            outfunc("Connection secure.")
        else:
            if config.secure:
                raise IOError, "Server is not able to handle a secure connection."
    except:
        outfunc(str(sys.exc_info()[1]))
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
