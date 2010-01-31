import re

namelist = []

def checknick(nick):
    if (len(nick) < 1 or
        len(nick) > 10 or
        nick == "tehsrvr" or #that one is permanently reserved for server use
        re.compile('[^a-zA-Z0-9]').search(nick) or
        nickregistered(nick)):
        return 1
    else:
        return 0

def registernick(nick):
    if checknick(nick):
        return 1
    else:
        namelist.append(nick)
        return 0

def freenick(nick):
    namelist.remove(nick)
    return

def changenick(old, new):
    if nickregistered(new): return 1
    if freenick(old) or registernick(new):
        return 0

def nickregistered(nick):
    collision = 0
    for usedname in namelist:
        if nick == usedname:
            collision = 1
    return collision

def nicklist():
    return namelist
 
