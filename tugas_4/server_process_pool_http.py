from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

#untuk menggunakan processpoolexecutor, karena tidak mendukung subclassing pada process,
#maka class ProcessTheClient dirubah dulu menjadi function, tanpda memodifikasi behaviour didalamnya

def ProcessTheClient(connection, address):
    rcv = ""
    while True:
        try:
            data = connection.recv(1024)  # ukuran buffer diperbesar
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

    my_socket.bind(('0.0.0.0', 8889))
    my_socket.listen(20)

    with ProcessPoolExecutor(max_workers=20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            #logging.warning("connection from {}".format(client_address))
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)
            #menampilkan jumlah process yang sedang aktif
            jumlah = ['x' for i in the_clients if i.running()]
            print(jumlah)

def main():
    Server()

if __name__ == "__main__":
    main()
