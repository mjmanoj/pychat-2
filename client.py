import socket, thread, string

try:
    #if you want to use a server other than localhost, add a file
    #named serverinfo.py in the same directory as this file with
    #one line: IP = '12.34.56.789' #change to the desired ip...
    from serverinfo import IP
except:
    #if there is no serverinfo.py file, just use localhost
    IP = 'localhost'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
def inputthread(s, infunc):
    while 1:
        s.send("\xaa" + infunc())
 
def netmanager(s, outfunc, infunc, killfunc):
    while 1:
        command = s.recv(1024)
        if len(command) == 0:
            command = '!TERMINATE'
        if not command.startswith("!"):
            outfunc(command)
        elif command.startswith("!NOTE"):
            outfunc(string.replace(command, "!NOTE ", "Server: "))
        elif command.startswith("!SENDNICK"):
            s.send(infunc("Enter nickname: "))
        elif command.startswith("!CHATMODE"):
            outfunc("Entering chat mode at server's request.")
            thread.start_new_thread(inputthread, (s, infunc))
        elif command.startswith("!TERMINATE"):
            outfunc("Client terminated by server...")
            s.close()
            killfunc()
 
def callbacks(outfunc, infunc, killfunc):
    s.connect((IP, 59387))
    netmanager(s, outfunc, infunc, killfunc)

def main():
    def printfunc(text): print text #print is not a function
    callbacks(printfunc, raw_input, exit)

if __name__ == '__main__':
    main()
