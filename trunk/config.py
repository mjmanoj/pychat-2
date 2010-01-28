import sys, socket, thread, time

certfile = None #this one could be set in either file, so it needs special treatment

#load client settings
try:    from serverinfo import IP
except: IP = 'localhost'
try:    from serverinfo import secure
except: secure = False
try:    from serverinfo import configuredtoserve
except: configuredtoserve = False
try:    from serverinfo import certfile
except: pass

#load server settings
try:    from serverconf import hascert
except: hascert = False
try:    from serverconf import forceencryption
except: forceencryption = False
try:    from serverconf import certfile
except: pass

if certfile == None:
    certfile = 'cert.pem'

#load global settings
try:    from commonconf import devmode
except: devmode = False

#find out if tls/ssl can be used
sslavailable = True
try:
    import ssl
except:
    sslavailable = False

class serverconf():
    #This is really a namespace. It should be considered read-only!
    def __init__(self):
        if not sslavailable:
            print "Warning: SSL module not available. Encryption cannot be used."
        self.certfile = certfile
        self.forceencryption = forceencryption
        self.sslavailable = sslavailable
        self.canserve = hascert
        self.devmode = devmode

class clientconf():
    #This is really a namespace. It should be considered read-only!
    def __init__(self):
        if secure and not sslavailable:
            print "Warning: SSL module not available. Encryption cannot be used."
        self.sslavailable = sslavailable
        self.secure = secure
        self.IP = IP
        self.canserve = configuredtoserve
        self.certfile = certfile
        self.devmode = devmode
