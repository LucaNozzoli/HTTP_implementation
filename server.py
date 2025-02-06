#!/usr/bin/env python

import socket
import os
import _thread
import hashlib
import time

SERVER_TCP_IP = '127.0.0.1'
SERVER_TCP_PORT = 4000
SERVER_BUFFER_SIZE = 1024

client_threads = _thread.allocate_lock()

endpoints = {
    "/": "base.html",
    "/sample":"sample.html",
    "/utfpr": "./images/utfpr.jpeg",
    "/london": "./images/london.jpg"
}


def connection_handling(connection, address) -> bool:
    while True:
        content = connection.recv(SERVER_BUFFER_SIZE)
        if not content:
            break
        message = content.decode()
        request = message.split("Host")[0].strip()  # Strip any extra whitespace

        print("Request received:", message)

        for endpoint, filename in endpoints.items():
            if request.startswith(f"GET {endpoint} HTTP/1.1"):
                print("Matching endpoint found:", endpoint)
                if os.path.exists(filename):
                    if filename.endswith(".html"):
                        with open(filename, "r", encoding="utf-8") as file:
                            file_body = file.read()

                        response_status = "HTTP/1.1 200 OK\r\n"
                        response_header = f"Content-Type: text/html; charset=utf-8\r\nContent-Length: {len(file_body.encode('utf-8'))}\r\n\r\n"

                        response = (response_status + response_header + file_body).encode("utf-8")

                    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
                        with open(filename, "rb") as file:
                            file_body = file.read()

                        response_status = "HTTP/1.1 200 OK\r\n"
                        response_header = f"Content-Type: image/jpeg\r\nContent-Length: {len(file_body)}\r\n\r\n"

                        response = (response_status + response_header).encode("utf-8") + file_body

                    else:
                        error_message = "HTTP/1.1 400 Bad Request\r\n\r\n"
                    connection.sendall(response)
                    break  # Exit the loop if matched

        else:
            error_message = "HTTP/1.1 404 Not Found\r\n\r\n"
            connection.sendall(error_message.encode("utf-8"))

        connection.close()
        return True


def Main():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_TCP_IP, SERVER_TCP_PORT))
    sock.listen()
    print(f"Server up and listening on port {SERVER_TCP_PORT}")

    
    while True:
        connection, address = sock.accept()
        print("New connection created on: ", address)
        client_threads.acquire()

        _thread.start_new_thread(connection_handling, (connection, address))
        
        client_threads.release()
        
Main()
