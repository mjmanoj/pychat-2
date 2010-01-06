import socket, thread, string, sys, time

try:
    #if you want to use a server other than localhost, add a file
    #named serverinfo.py in the same directory as this file with
    #one line: IP = '12.34.56.789' #change to the desired ip...
    from serverinfo import IP
except:
    #if there is no serverinfo.py file, just use localhost
    IP = 'localhost'

global buffertext, bufferfull
bufferfull = 0
buffertext = ''

global socketclosed
socketclosed = 0

def inputthread(infunc):
    global bufferfull, buffertext, socketclosed
    while 1:
        if socketclosed: return
        localbuf = infunc()
        while bufferfull:
            time.sleep(0.01) #wait until the buffer is empty
            if socketclosed: return
        buffertext = localbuf
        bufferfull = 1

def sendthread(s):
    global bufferfull, buffertext, socketclosed
    while 1:
        if bufferfull:
            s.send("\xaa" + buffertext)
            buffertext = ''
            bufferfull = 0
        else:
            time.sleep(0.01)
            if socketclosed:
                s.close()
                return

def netmanager(s, outfunc, infunc, killfunc):
    global socketclosed
    while 1:
        command = s.recv(1024)
        if len(command) == 0:
            command = '!TERMINATE'
        if not command.startswith("!"):
            outfunc(command)
        elif command.startswith("!CHATMODE"):
            outfunc("Nickname accepted, entering chat mode.")
            thread.start_new_thread(sendthread, tuple([s]))
            thread.start_new_thread(inputthread, tuple([infunc]))
        elif command.startswith("!NOTE"):
            outfunc(string.replace(command, "!NOTE ", "Server: "))
        elif command.startswith("!TERMINATE"):
            outfunc("Client terminated.")
            s.close()
            socketclosed = 1
            killfunc()
            return

def callbacks(outfunc, infunc, killfunc, server=IP):
    nick = (infunc("Enter nickname: "))
    outfunc("Connecting...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((IP, 59387))
    except:
        outfunc("Could not connect to server: " + str(sys.exc_info()[1]))
        killfunc()
    outfunc("Server found.")
    s.send(nick)
    netmanager(s, outfunc, infunc, killfunc)

def main():
    def printfunc(text): print text #print is not a function in 2.5 and earlier
    callbacks(printfunc, raw_input, exit)

if __name__ == '__main__':
    main()
