import socket
import sys

from helpers.customPrint import rs_print as xprint
from helpers.loadFromFile import loadFromFile

PORT = 60020

TS1Port = 6030
TS2Port = 6031

TS1socket = None
TS2socket = None

dnsRecords = {}


# Establishes connection to both TS servers
def connectToTS(ts1_HN, ts2_HN):
    sa_sameas_myaddr = socket.gethostbyname(socket.gethostname())

    global TS1socket, TS2socket

    try:
        TS1socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TS2socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        xprint("Created both TS sockets")
    except socket.error as err:
        xprint("Unable to create TS sockets", err)

    TS1socket.connect((ts1_HN, TS1Port))
    TS2socket.connect((ts2_HN, TS2Port))


# Performs a DNS lookup on external connection
def lookupExternal(query, connection):
    connection.send(query.encode("utf-8"))
    return connection.recv(100).decode('utf-8')


# Performs local lookup
# If not found, performs external lookup based on domain postfix
def lookupHostname(query):

    hostname = query.strip()

    # Hostname is in DNS records
    if hostname in dnsRecords:
        entry = dnsRecords[hostname]
        return hostname + " " + entry["ip"] + " " + entry["flag"]

    domaintype = hostname.split('.')[-1]

    if domaintype == 'com':
        xprint("\tPerforming com TS server lookup for", hostname)
        return lookupExternal(hostname, TS1socket)
    if domaintype == 'edu':
        xprint("\tPerforming edu TS server lookup for", hostname)
        return lookupExternal(hostname, TS2socket)

    # Hostname not in DNS records
    return hostname + ' - Error:HOST NOT FOUND'


def handleAuth(params, csockid):

    print(params)

    TS1socket.send(('auth^^' + params[1]).encode('utf-8'))
    ts1res = TS1socket.recv(100).decode('utf-8')

    TS2socket.send(('auth^^' + params[1]).encode('utf-8'))
    ts2res = TS2socket.recv(100).decode('utf-8')

    if ts1res == params[2]:
        response = 'TLDS1'
    elif ts2res == params[2]:
        response = 'TLDS2'
    else:
        response = 'NO_DIGEST_MATCH'

    csockid.send(response.encode('utf-8'))

# Starts server
def startServer():
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        xprint("Socket Created")
    except socket.error as err:
        xprint("Error Opening Socket", err)
        exit(10)

    connection.bind(('', PORT))
    connection.listen(1)

    host = socket.gethostname()
    xprint("Hostname:", host)

    localhost_ip = (socket.gethostbyname(host))
    xprint("IP:", localhost_ip)

    return connection


# Service that listens for client requests
def runService(connection, ts1_HN, ts2_HN):

    connectToTS(ts1_HN, ts2_HN)

    csockid, addr = connection.accept()
    xprint("Got connection request from", str(addr))

    try:
        while True:
            query = csockid.recv(100).decode('utf-8')
            if len(query) < 1:
                continue
            #xprint("Message from client:", query)

            params = query.strip().split('^^')
            if params[0] == 'auth':
                handleAuth(params, csockid)

            #resolved = lookupHostname(query)
            #xprint("\tReplying with", resolved)
            #csockid.send(resolved.encode('utf-8'))
    except socket.error:
        xprint("No more data, closing connection")
        pass


# Loads file into local DNS data structure
def loadFile(dns_FILE):
    # Read file into data structure
    with open(dns_FILE, "r") as dnsFile:
        global dnsRecords
        dnsRecords = loadFromFile(dnsFile)
        xprint("Loaded " + dns_FILE)


def main(ts1_HN, ts2_HN):

    connection = startServer()

    runService(connection, ts1_HN, ts2_HN)

    connection.close()


main('localhost', 'localhost')
