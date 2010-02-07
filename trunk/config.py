certfile = None #this one could be set in either file, so it needs special treatment

def getvalue(name, default):
    #returns the value of the variable named by name, if it is defined.
    #otherwise, it returns the contents of default
    try:
        return eval(name)
    except:
        return default

#load client settings
try:    import serverinfo as clientconf
except: pass
IP                  = getvalue('clientconf.IP',                'localhost')
secure              = getvalue('clientconf.secure',            False)
configuredtoserve   = getvalue('clientconf.configuredtoserve', False)
certfile            = getvalue('clientconf.certfile',          'cert.pem')

#load server settings
try:    import serverconf
except: pass
hascert         = getvalue('serverconf.hascert',            configuredtoserve)
forceencryption = getvalue('serverconf.forceencryption',    False)
certfile        = getvalue('serverconf.certfile',           certfile)

#load global settings
try:    import commonconf
except: pass
devmode = getvalue('commonconf.devmode', False)

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
