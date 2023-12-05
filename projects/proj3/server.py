# author: Jessica Scheier

import socket
import json
import random
import datetime
import hashlib
import sys

sessions = {}

def log_to_server(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print(f"SERVER LOG: {timestamp} {message}")

def post(request, accounts):
    headers, body = request.split("\r\n\r\n", 1)
    headers = headers.split("\r\n")

    username = ""
    password = ""
    for header in headers:
        if "username" in header:
            str, username = header.split(": ")
        if "password" in header:
            str, password = header.split(": ")

    if username == "" or password == "":
        log_to_server("LOGIN FAILED")
        return "501 Not Implemented", "", ""

    if is_valid(username, password, accounts):
        session_id = get_session_id() # "0x"+hex(random.getrandbits(64))[2:]
        sessions[session_id] = [username, datetime.datetime.now().timestamp()]
        # print(sessions)
        cookie = f"Set-Cookie: sessionID={session_id}"
        log_to_server(f"LOGIN SUCCESSFUL: {username} : {password}")
        return "200 OK", cookie, "Logged in!"
    else:
        log_to_server(f"LOGIN FAILED: {username} : {password}")
        return "200 OK", "", "Login failed!"
    
def get_session_id():
    return "0x"+hex(random.getrandbits(64))[2:]

def is_valid(username, password, accounts_file):
    with open(accounts_file) as file:
        accounts = json.load(file)

    if username in accounts:
        hashed, salt = accounts[username]
        test = hashlib.sha256((password + salt).encode('ascii')).hexdigest()
        return test == hashed

    return False

def get_request(request, session_timeout, root_dir, target):
    headers = request.split("\r\n")

    cookie = ""
    for header in headers:
        if "Cookie" in header:
            str, cookie = header.split(": ")
            cookie = cookie.split("=")[1].strip()
    
    if cookie == "":
        return "401 Unauthorized", ""
    
    if cookie in sessions:
        username = sessions[cookie][0]
        timestamp = sessions[cookie][1]
        # print(timestamp)
        current_time = datetime.datetime.now().timestamp()
        if (current_time - timestamp >= session_timeout):
            log_to_server(f"SESSION EXPIRED: {username} : {target}")
            return "401 Unauthorized", ""
        else:
            sessions[cookie][1] = current_time
            # print(sessions[cookie])
            exists = False
            try:
                with open(root_dir+username+target, 'rb'):
                    pass
                exists = True
            except FileNotFoundError:
                exists = False
            if (exists):
                with open(root_dir+username+target, 'rb') as file:
                    content = file.read().decode()
                log_to_server(f"GET SUCCEEDED: {username} : {target}")
                return "200 OK", content
            else:
                log_to_server(f"GET FAILED: {username} : {target}")
                return "404 NOT FOUND", ""
    else:
        log_to_server(f"COOKIE INVALID: {target}")
        return "401 Unauthorized", ""

def start_server(ip, port, accounts, session_timeout, root_dir):
    ip = sys.argv[1]
    port = int(sys.argv[2])
    accounts = sys.argv[3]
    session_timeout = int(sys.argv[4])
    root_dir = sys.argv[5]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.listen()

    while True:
        conn, addr = sock.accept()
        with conn:
            request = conn.recv(1024).decode()
            http_method = request.split(" ")[0]
            request_target = request.split(" ")[1]
            http_version = "HTTP/1.0"

            if http_method == "POST" and request_target == "/":
                status, headers, body = post(request, accounts)
                message = http_version + " " + status + "\r\n" + headers + "\r\n\r\n" + body
                conn.sendall(message.encode())
            elif http_method == "GET":
                status, body = get_request(request, session_timeout, root_dir, request_target)
                if (len(body) == 0):
                    message = f"{http_version} {status}\r\n\r\n"
                else:
                    message = f"{http_version} {status}\r\n\r\n{body}"
                conn.sendall(message.encode())
            else:
                message = f"{http_version} 501 Not Implemented\r\n\r\n"
                conn.sendall(message.encode())

        conn.close()

def main():
    start_server(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5])

main()