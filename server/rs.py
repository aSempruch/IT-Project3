import socket
from helpers.customPrint import rs_print as xprint
from helpers.loadFromFile import loadFromFile

PORT = 60020
DNS_FILE = '../PROJ2-DNSRS.txt'
DNS_COM = 'localhost:'

TS1Port = 6030
TS2Port = 6031

TS1socket = None
TS2socket = None

dnsRecords = {}

def connectToTS():
    sa_sameas_myaddr = socket.gethostbyname(socket.gethostname())

    global TS1socket, TS2socket

    try:
        TS1socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TS2socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        xprint("Created both TS sockets")
    except socket.error as err:
        xprint("Unable to create TS sockets", err)

    TS1socket.connect((sa_sameas_myaddr, TS1Port))
    TS2socket.connect((sa_sameas_myaddr, TS2Port))

def lookupExternal(query, connection):
    connection.send(query.encode("utf-8"))
    return connection.recv(100).decode('utf-8')

def lookupHostname(query):

    hostname = query.strip()

    # Hostname is in DNS records
    if hostname in dnsRecords:
        entry = dnsRecords[hostname]
        return hostname + " " + entry["ip"] + " " + entry["flag"]

    domaintype = hostname.split('.')[-1]

    if domaintype == 'com':
        xprint("Performing com TS server lookup for", hostname)
        return lookupExternal(hostname, TS1socket)
    if domaintype == 'edu':
        xprint("Performing edu TS server lookup for", hostname)
        return lookupExternal(hostname, TS2socket)

    # Hostname not in DNS records
    return hostname + ' - Error:HOST NOT FOUND'

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

def runService(connection):

    connectToTS()

    csockid, addr = connection.accept()
    xprint("Got connection request from", str(addr))

    try:
        while True:
            query = csockid.recv(100).decode('utf-8')
            if len(query) < 1:
                continue
            xprint("Lookup from client:", query)
            resolved = lookupHostname(query)
            xprint("Replying with", resolved)
            csockid.send(resolved.encode('utf-8'))
    except socket.error:
        xprint("No more data, closing connection")
        pass

def loadFile():
    # Read file into data structure
    with open(DNS_FILE, "r") as dnsFile:
        global dnsRecords
        dnsRecords = loadFromFile(dnsFile)
        xprint("Loaded " + DNS_FILE)

def main():

    loadFile()

    connection = startServer()

    # Accept multiple connections
    while True:
        runService(connection)

    connection.close()

main()