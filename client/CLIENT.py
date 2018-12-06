import socket, sys, hmac

RS_PORT = 60020
TS_PORT = 60030

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
        print("Created both TS sockets")
    except socket.error as err:
        print("Unable to create TS sockets", err)

    TS1socket.connect((ts1_HN, TS1Port))
    TS2socket.connect((ts2_HN, TS2Port))

def rs_connect(hostName):
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Created client socket")
    except socket.error as err:
        print("Unable to create socket", err)

    connection.connect((hostName, RS_PORT))

    return connection


def lookup(line, connection):
    connection.send(('lookup^^'+line).encode("utf-8"))
    return connection.recv(100).decode('utf-8')

def authenticate(key, challenge, connection):
    digest = hmac.new(key.encode(), challenge.encode("utf-8"))
    connection.send(('auth^^' + challenge + '^^' + digest.hexdigest()).encode('utf-8'))
    response = connection.recv(100).decode('utf-8')
    print(key, response)
    return response

def main(hostName, fileName):
    rs_connection = rs_connect(hostName)
    connectToTS('localhost', 'localhost')

    with open(fileName) as hostsFile, open('RESOLVED.txt', 'w+') as resolvedFile:
        for line in hostsFile:
            split = line.strip().split(' ')
            key = split[0]
            challenge = split[1]
            domainName = split[2]
            authresponse = authenticate(key, challenge, rs_connection)
            print("HERE")
            if authresponse == 'TLDS1':
                tsServer = TS1socket
            elif authresponse == 'TLDS2':
                tsServer = TS2socket
            else:
                print('Error for', line)
                continue

            resolved = lookup(split[2], tsServer)
            print(resolved)
            #print("RS Lookup for " + line + ": " + response)
            #resolvedFile.write(response + '\n')
            #print(line)

    rs_connection.close()


main('localhost', 'PROJ3-HNS.txt')
