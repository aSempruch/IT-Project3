import socket, sys, hmac

RS_PORT = 60020
TS_PORT = 60030


def rs_connect(hostName):
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Created client socket")
    except socket.error as err:
        print("Unable to create socket", err)

    connection.connect((hostName, RS_PORT))

    return connection


def lookup(line, connection):
    connection.send(line.encode("utf-8"))
    return connection.recv(100).decode('utf-8')

def authenticate(key, challenge, connection):
    digest = hmac.new(key.encode(), challenge.encode("utf-8"))
    connection.send(('auth^^' + challenge + '^^' + digest.hexdigest()).encode('utf-8'))


def main(hostName, fileName):
    rs_connection = rs_connect(hostName)

    with open(fileName) as hostsFile, open('RESOLVED.txt', 'w+') as resolvedFile:
        for line in hostsFile:
            split = line.strip().split(' ')
            key = split[0]
            challenge = split[1]
            domainName = split[2]
            authresponse = authenticate(key, challenge, rs_connection)
            #print("RS Lookup for " + line + ": " + response)
            #resolvedFile.write(response + '\n')
            #print(line)

    rs_connection.close()


main('localhost', 'PROJ3-HNS.txt')
