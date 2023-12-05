# authors: Jessica Scheier and Archisa Bhattacharya

import socket
import sys
import hashlib

# HOST, PORT = "127.0.0.1", 1236

# def readLine(conn):
#     # "read a line from a socket"
#     chars = []
#     while True:
#         a = conn.recv(1)
#         chars.append(a)
#         if a == "\n" or a == "":
#             return "".join(chars)

def readLine(conn):
    # "read a line from a socket"
    chars = []
    while True:
        a = conn.recv(1)
        if a == b"\n" or a == b"":
            return b"".join(chars).decode('ascii')
        chars.append(a)

def escape(s):
    return s.replace(b".", b"\\.")


def main():
    # Start the client
    server = sys.argv[1]
    port = int(sys.argv[2])
    msgFile = sys.argv[3]
    sigFile = sys.argv[4]

    # Open the message file from the name in the command line
    # While there is still more data in the message file:
    # Read in one line
    # Convert the string into the number of bytes
    # Read in the number of bytes from the message file into a byte string or byte array
    # Append the bytes of the message into an array of messages
    count = 0
    with open(msgFile, 'r') as f:
        # Read all the lines of the file into a list

        # count = 0
        messages = []
        while True:
            count += 1

            # Get next line from file
            line = f.readline()

            # if line is empty
            # end of file is reached
            if not line:
                break
            # print("Line{}: {}".format(count, line.strip()))
            # line = line.strip()  # Strip any trailing newline or space characters
            byte_line = line.encode('ascii')  # Convert the string into bytes
            messages.append(byte_line)

        f.close()
    # print(messages)

    # Open the signature file from the name in the command line
    # While there is still more data in the signature file:
    # Read in one line
    # Append the string of the signature into an array of signatures
    with open(sigFile, 'r') as sFile:
        # Read all the lines of the file into a list
        signatures = sFile.readlines()
        # print("sig: ")
    # print(signatures)

    # Open a TCP socket to the server using the name and port from the command line
    # Send a ìHELLOî message to the server
    # Read the response
    # If the response is not ì260 OKî, print an error and end the program.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((server, port))

    message1 = "HELLO\n"
    s.sendall(message1.encode('ascii'))

    responseForHello = s.recv(1024)
    print(responseForHello.decode('ascii').strip()) # is this the first 260?

    if responseForHello.decode('ascii') != "260 OK\n":
        print("client ... unexpected response, exiting ...\n")
        return

    # Set a message counter variable to zero
    counter = 0

    # Foreach message in the array of messages:
    # Send the DATA command in one line on the TCP socket
    # Send the message on the TCP socket
    # Read a line from the server from the TCP socket
    # If the response is not 270 SIG, print an error and end the program.
    # Read another line from the server
    # Compare the string from the server with the signature string stored in the array
    # signatures for this message at the message counter number
    # If the strings match:
    # send a PASS message to server
    # Else:
    # send a FAIL message to the server
    # Read a line from the server
    # If the response is not 260 OK, print an error and end the program.
    # Increment the message counter
    for i in range(1, count, 2):
        s.sendall(b"DATA\n")
        s.sendall(escape(messages[i])+b'\n.\n')
        # print(escape(messages[i])+b'\n.\n')

        wait_for_270 = readLine(s)
        print(wait_for_270)
        if wait_for_270 != "270 SIG":
            print("client ... unexpected response, exiting ...\n")
            return
        received_signature = readLine(s)
        print(received_signature)
        if received_signature.strip() != signatures[counter].strip():
            s.sendall(b"FAIL\n")
        else:
            s.sendall(b"PASS\n")
        wait_for_260 = readLine(s)
        print(wait_for_260)

        if wait_for_260 != "260 OK":
            print("client ... unexpected response, exiting ...\n")
            return
        else:
            counter = counter + 1

    # Send a QUIT message to the server
    quit_message = "QUIT\n"
    s.sendall(quit_message.encode('ascii'))
    # Close the TCP socket.
    s.close()

if __name__ == '__main__':
    main()
