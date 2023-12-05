# authors: Jessica Scheier and Archisa Bhattacharya

import sys
import socket
import hashlib

#HOST, PORT = "127.0.0.1", 1236


def readLine(conn):
    # "read a line from a socket"
    chars = []
    while True:
        a = conn.recv(1)
        if a == b"\n" or a == b"":
            return b"".join(chars).decode('ascii')
        chars.append(a)

def read_msg(conn):
    chars = []
    while True:
        a = conn.recv(1)
        if a == b"\n":
            chars.append(a)
            return b"".join(chars).decode('ascii')
        chars.append(a)

def unescape(s):
    return s.replace("\\.", ".")


def main():
    # Start the server
    hostIP = socket.gethostbyname("localhost")
    port = int(sys.argv[1])
    keyFile = sys.argv[2]
    
    CMD_HELLO = "HELLO"
    CMD_DATA = "DATA"
    CMD_QUIT = "QUIT"

    # Read in all keys from keyfile
    with open(keyFile, 'r') as file:
        # Read all the lines of the file into a list
        key_lines = file.readlines()
    # print(key_lines)

    # Open a TCP socket on the port and start to listen
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((hostIP, port))
    sock.listen()

    buf = ""
    alive = False
    keepRunning = True
    count = -1

    while keepRunning:
        if not alive:
            # When the connection completes, read a line from the returned connected socket
            (conn, address) = sock.accept()
            alive = True
            # print("server ... having an alive connection now ... \n")
            # Read first line and check for HELLO
            firstLine = readLine(conn)
            # print("server ... firstLine = [" + firstLine + "]\n")
            if firstLine != "HELLO":
                conn.close()
                keepRunning = False
                alive = False
                print("server ... Exiting : firstLine = [" + firstLine + "]\n")
                # for some reason sys.exit wont work in the autograder
                # sys.exit(1)
                return
            else:
                print("HELLO")
                reply = b"260 OK\n"
                conn.sendall(reply)
                continue
        else:
            # read the data byte by byte
            data = conn.recv(1)
            if not data:
                alive = False
                continue
            # read until the newline character
            data = chr(data[0])
            if data != '\n':
                buf += data
                continue
            # print("server ... received buffer ... " + buf + "\n")

            if (buf[:len(CMD_DATA)] == CMD_DATA):
                print("DATA")
                while True:
                    sha_hash = hashlib.sha256()
                    msg_line = read_msg(conn) # conn.recv(1024).decode('ascii').strip()
                    # read message in byte by byte, if there's a newline stop^
                    msg_line = msg_line.strip()
                    msg_line = unescape(msg_line)
                    print(msg_line)
                    read_again = conn.recv(1024) # read in .\n
                    read_again = read_again.strip()
                    print(read_again.decode('ascii'))
                    if msg_line.strip() == ".":
                        break
                    sha_hash.update(msg_line.encode('ascii'))
                    count += 1
                    sha_hash.update(key_lines[count].strip().encode('ascii'))
                    signature = sha_hash.hexdigest()
                    conn.sendall("270 SIG\n".encode('ascii'))
                    s = f"{signature}\n".encode('ascii')
                    conn.sendall(s)
                    response = conn.recv(1024).decode('ascii').strip()
                    print(response)
                    if response not in ["PASS", "FAIL", "PASS\n", "FAIL\n"]:
                        print("Error: invalid response from client. Closing program.")
                        conn.close()
                        return
                    conn.sendall("260 OK\n".encode('ascii'))
                    break
                buf = ""

            elif (buf[:len(CMD_QUIT)] == CMD_QUIT):
                print("QUIT")
                conn.close()
                return
            
            else:
                print("ERROR: unexpected response from the client")
                conn.close()
                return
                
if __name__ == '__main__':
    main()
