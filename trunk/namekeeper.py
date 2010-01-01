namelist = []
def register(nick):
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

def free(nick):
    namelist.remove(nick)
    return

def change(old, new):
    namelist.remove(old)
    namelist.append(new)

def registered(nick):
    collision = 0
    for usedname in namelist:
        if nick == usedname:
            collision = 1
    return collision

def getlist():
    return namelist
 
