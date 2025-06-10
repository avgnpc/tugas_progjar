from socket import *
import socket
import threading
import logging
from datetime import datetime

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        try:
            while True:
                data = self.connection.recv(1024)
                if data:
                    request = data.decode().strip()
                    logging.warning(f"Request from {self.address}: {request}")
                    
                    if request == "TIME":
                        now = datetime.now()
                        jam = now.strftime("%H:%M:%S")
                        response = f"JAM {jam}\r\n"
                        self.connection.sendall(response.encode('utf-8'))
                    
                    elif request == "QUIT":
                        logging.warning(f"Client {self.address} requested to quit.")
                        break
                    
                    else:
                        self.connection.sendall(b"Invalid command\r\n")
                else:
                    break
        except Exception as e:
            logging.error(f"Error with client {self.address}: {e}")
        finally:
            self.connection.close()

class Server(threading.Thread):
    def __init__(self):
        self.clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', 45000))
        self.my_socket.listen(5)
        logging.warning("Server listening on port 45000...")
        while True:
            connection, client_address = self.my_socket.accept()
            logging.warning(f"Connection from {client_address}")
            clt = ProcessTheClient(connection, client_address)
            clt.start()
            self.clients.append(clt)

def main():
    svr = Server()
    svr.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
