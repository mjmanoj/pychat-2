namelist = []
def registernick(nick):
    collision = 0
    if len(nick) < 1 or nick == "tehsrvr": #that one is permenantly reserved for server use
        return 1
    for usedname in namelist:
        if nick == usedname:
            collision = 1
    if collision:
        return 1
    else:
        namelist.append(nick)
        return 0

def freenick(nick):
    namelist.remove(nick)
    return

def changenick(old, new):
    namelist.remove(old)
    namelist.append(new)

def nickregistered(nick):
    collision = 0
    for usedname in namelist:
        if nick == usedname:
            collision = 1
    return collision

def nicklist():
    return namelist
 
