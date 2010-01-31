import os, sys, string

#make a messages directory if it doesn't exist
try:
    os.listdir('.').index('messages')
    os.listdir('messages')
except:
    os.mkdir('messages')

def checkfilename(title):
    for c in title:
        for i in r'/\?%*:"<>.':
            if c == i:
                return "Char \"%s\" not allowed in title!" % c
    return 0

def postmessage(title, contents):
    checkresult = checkfilename(title)
    if checkresult != 0:
        return checkresult
    if len(contents) > 600:
        return "Messages cannot be longer than 600 letters. Yours is %d letters too long." % len(contents)-600
    try:
        open('messages/'+title, 'w').write(contents)
        return 'Message posted'
    except:
        return str(sys.exc_info()[1])

def countmessages():
    try:
        return len(os.listdir('messages'))
    except:
        return str(sys.exc_info()[1])

def listmessages():
    try:
        return string.join(os.listdir('messages'), ', ')
    except:
        return str(sys.exc_info()[1])

def readmessage(title):
    checkresult = checkfilename(title)
    if checkresult != 0:
        return checkresult
    try:
        return open('messages/'+title, 'r').read(600)
    except:
        return str(sys.exc_info()[1])

def delmessage(title):
    checkresult = checkfilename(title)
    if checkresult != 0:
        return checkresult
    try:
        os.remove('messages/'+title)
        return 'Message deleted.'
    except:
        return str(sys.exc_info()[1])

