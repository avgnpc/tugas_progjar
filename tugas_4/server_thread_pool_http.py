
from socket import *
import socket
import time
import sys
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = ""
    while True:
        try:
            data = connection.recv(1024)  # perbesar buffer
            if data:
                d = data.decode()
                rcv = rcv + d
                if "\r\n\r\n" in rcv:
                    hasil = httpserver.proses(rcv)
                    hasil = hasil + "\r\n\r\n".encode()
                    connection.sendall(hasil)
                    rcv = ""
                    connection.close()
                    return
            else:
                break
        except OSError:
            pass
    connection.close()
    return

def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind(('0.0.0.0', 8885))
    my_socket.listen(20)

    with ThreadPoolExecutor(max_workers=20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)
            jumlah = ['x' for i in the_clients if i.running()]
            print(jumlah)

def main():
    Server()

if __name__ == "__main__":
    main()
