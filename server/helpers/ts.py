import socket, hmac, threading
from helpers.customPrint import ts_print as xprint
from helpers.loadFromFile import loadFromFile

dnsRecords = {}
key = None


# Performs local hs lookup
def lookupHostname(query):

    hostname = query.strip()

    # Hostname is in DNS records
    if hostname in dnsRecords:
        xprint("Looking up", hostname)
        entry = dnsRecords[hostname]
        return hostname + " " + entry["ip"] + " " + entry["flag"]

    # Hostname not in DNS records
    return hostname + ' - Error:HOST NOT FOUND'


# Starts server
def startServer(PORT):
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
def runService(csockid, addr):

    xprint("Got connection request from", str(addr))

    try:
        while True:
            query = csockid.recv(100).decode('utf-8')
            if len(query) < 1:
                continue
            params = query.strip().split('^^')

            if params[0] == 'auth':
                digest = hmac.new(key.encode(), params[1].encode("utf-8"))
                csockid.send(digest.hexdigest().encode('utf-8'))
                continue

            xprint("Lookup from client:", params[1])
            response = lookupHostname(params[1])
            xprint("Sending to client: " + response)
            csockid.send(response.encode('utf-8'))
    except:
        xprint("No more data, closing connection")
        pass


# Loads DNS records and key from file
def loadFile(DNS_FILE, KEY_FILE):
    #Read Key
    with open(KEY_FILE, "r") as keyFile:
        global key
        key = keyFile.readline().strip()

    # Read file into data structure
    with open(DNS_FILE, "r") as dnsFile:
        global dnsRecords
        dnsRecords = loadFromFile(dnsFile)
        xprint("Loaded " + DNS_FILE)


def main(port, dnsFile, keyFile):

    loadFile(dnsFile, keyFile)

    connection = startServer(port)

    while True:
        csockid, addr = connection.accept()
        threading.Thread(target=runService(csockid, addr))

    connection.close()