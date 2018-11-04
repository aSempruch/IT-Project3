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


def lookup(line, connection):
    connection.send(line.encode("utf-8"))
    return connection.recv(100).decode('utf-8')

def main():
    rs_connection = rs_connect()

    with open('../PROJ2-HNS.txt') as hostsFile, open('../RESOLVED.txt', 'w+') as resolvedFile:
        for line in hostsFile:
            line = line.strip()
            response = lookup(line, rs_connection)
            print("RS Lookup for " + line + ": " + response)
            resolvedFile.write(response + '\n')

    rs_connection.close()



main()