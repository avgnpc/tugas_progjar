import sys
import socket
import json
import logging
import ssl
import os
import base64

server_address = ('172.16.16.101', 8885)  # sesuaikan IP dan port server

def make_socket(destination_address='172.16.16.101', port=8885):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def make_secure_socket(destination_address='172.16.16.101', port=8885):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.load_verify_locations(os.getcwd() + '/domain.crt')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock, server_hostname=destination_address)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def send_command(command_str, is_secure=False, body_bytes=None):
    alamat_server = server_address[0]
    port_server = server_address[1]
    if is_secure:
        sock = make_secure_socket(alamat_server, port_server)
    else:
        sock = make_socket(alamat_server, port_server)

    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        if body_bytes:
            sock.sendall(command_str.encode() + body_bytes)
        else:
            sock.sendall(command_str.encode())

        data_received = ""
        while True:
            data = sock.recv(2048)
            if data:
                data_received += data.decode(errors='ignore')
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        return data_received
    except Exception as ee:
        logging.warning(f"error during data receiving {str(ee)}")
        return False

def interactive_menu():
    while True:
        print("\n===== MENU =====")
        print("1. Lihat daftar file di server")
        print("2. Upload file")
        print("3. Hapus file")
        print("4. Keluar")
        pilihan = input("Pilih (1-4): ").strip()

        if pilihan == '1':
            cmd = f"""GET /list HTTP/1.0\r\nHost: {server_address[0]}\r\n\r\n"""
            hasil = send_command(cmd)
            print(hasil)

        elif pilihan == '2':
            path_local = input("Path file lokal: ").strip()
            nama_remote = input("Nama file di server (misal: a.txt atau b/a.txt): ").strip()
            if not os.path.exists(path_local):
                print("File tidak ditemukan.")
                continue
            with open(path_local, "rb") as f:
                data = f.read()
            encoded = base64.b64encode(data)
            cmd = f"""POST /upload/{nama_remote} HTTP/1.0\r\nHost: {server_address[0]}\r\nContent-Length: {len(encoded)}\r\n\r\n"""
            hasil = send_command(cmd, body_bytes=encoded)
            print(hasil)

        elif pilihan == '3':
            path_remote = input("Path file yang ingin dihapus di server: ").strip()
            cmd = f"""DELETE /{path_remote} HTTP/1.0\r\nHost: {server_address[0]}\r\n\r\n"""
            hasil = send_command(cmd)
            print(hasil)

        elif pilihan == '4':
            print("Keluar.")
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == '__main__':
    interactive_menu()
