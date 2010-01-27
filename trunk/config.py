import sys, socket

#load server settings
try:    from serverconf import forceencryption
except: forceencryption = False
try:    from serverconf import certfile
except: certfile = 'cert.pem'

#load client settings
try:    from serverinfo import IP
except: IP = 'localhost'
try:    from serverinfo import secure
except: secure = False

#find out if tls/ssl can be used
sslavailable = True
try:
    import ssl
except:
    sslavailable = False

goodcert = True
try:
    if not sslavailable:
        raise IOError, ""
    ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_side=True, certfile=certfile, ssl_version=ssl.PROTOCOL_TLSv1)
except:
    print sys.exc_info()[1]
    goodcert = False

class serverconf():
    #This is really a namespace. It should be considered read-only!
    def __init__(self):
        if not sslavailable:
            print "Warning: SSL module not available. Encryption cannot be used."
        if not goodcert:
            print "Warning: Certificate could not be used. Encryption unavailable."
        self.certfile = certfile
        self.forceencryption = forceencryption
        self.sslavailable = sslavailable
        self.goodcert = goodcert

class clientconf():
    #This is really a namespace. It should be considered read-only!
    def __init__(self):
        self.sslavailable = sslavailable
        self.secure = secure
        self.IP = IP
