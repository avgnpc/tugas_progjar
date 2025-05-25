from socket import *
import socket
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from file_protocol import FileProtocol

fp = FileProtocol()

def handle_client(connection, address):
    logging.warning(f"Connection from {address}")
    buffer = ""
    try:
        while True:
            data = connection.recv(1024 * 1024)
            if not data:
                break
            buffer += data.decode()
            while "\r\n\r\n" in buffer:
                command, buffer = buffer.split("\r\n\r\n", 1)
                result = fp.proses_string(command)
                response = result + "\r\n\r\n"
                connection.sendall(response.encode())
    except Exception as e:
        logging.error(f"Error handling connection from {address}: {e}")
    finally:
        logging.warning(f"Connection closed from {address}")
        connection.close()

class Server:
    def __init__(self, ipaddress='127.0.0.1', port=6665, max_workers=5):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    def run(self):
        logging.warning(f"Server running at {self.ipinfo} with {self.pool._max_workers} threads")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        try:
            while True:
                connection, client_address = self.my_socket.accept()
                self.pool.submit(handle_client, connection, client_address)
        except KeyboardInterrupt:
            logging.warning("Server stopped manually by user")
        finally:
            self.my_socket.close()
            self.pool.shutdown(wait=True)

def main():
    port = 6666
    max_workers = 5
    if len(sys.argv) > 1:
        max_workers = int(sys.argv[1])
    svr = Server(ipaddress='127.0.0.1', port=port, max_workers=max_workers)
    svr.run()

if __name__ == "__main__":
    main()
