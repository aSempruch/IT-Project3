import socket

RS_PORT = 60020
TS_PORT = 60030

def rs_connect():
    sa_sameas_myaddr = socket.gethostbyname(socket.gethostname())

    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Created client socket")
    except socket.error as err:
        print("Unable to create socket", err)

    connection.connect((sa_sameas_myaddr, RS_PORT))

    return connection

def ts_connect(NS):
    #sa_sameas_myaddr = socket.gethostbyname(socket.gethostname())

    sa_sameas_myaddr = NS.split()[0]

    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Created client socket for TS server")
    except socket.error as err:
        print("Unable to create socket for TS server", err)

    connection.connect((sa_sameas_myaddr, TS_PORT))

    return connection

def lookup(line, connection):
    connection.send(line.encode("utf-8"))
    return connection.recv(100).decode('utf-8')

def main():
    rs_connection = rs_connect()
    ts_connection = None

    with open('../PROJI-HNS.txt') as hostsFile, open('../RESOLVED.txt', 'w+') as resolvedFile:
        for line in hostsFile:
            line = line.strip()
            response = lookup(line, rs_connection)
            print("RS Lookup for " + line + ": " + response)
            # Check for NS response
            if response.split()[2] == 'NS':
                print("RS server did not have " + line)
                if ts_connection is None:
                    ts_connection = ts_connect(response)
                response = lookup(line, ts_connection)
                print("TS Lookup for " + line + ": " + response)
            resolvedFile.write(response + '\n')

    rs_connection.close()
    if ts_connection != None:
        ts_connection.close()



main()