import socket
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

SERVER_IP = '127.0.0.1'
SERVER_PORT = 6666
BUFFER_SIZE = 1024 * 1024

def send_command(command, filedata_b64=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))

        if command.startswith("UPLOAD") and filedata_b64:
            parts = command.split(" ", 1)
            if len(parts) == 2:
                filename = parts[1]
                full_command = f"UPLOAD {filename} {filedata_b64}\r\n\r\n"
            else:
                raise ValueError("UPLOAD command missing filename")
        else:
            full_command = command + "\r\n\r\n"

        s.sendall(full_command.encode())

        # receive response
        response = b""
        while True:
            data = s.recv(1024)
            if not data:
                break
            response += data
            if b"\r\n\r\n" in response:
                break
        return response.strip()


def worker_task(op, filename=None):
    start_time = time.time()
    byte_count = 0

    if op == "list":
        response = send_command("LIST")
        byte_count = len(response)
    elif op == "download" and filename:
        response = send_command(f"GET {filename}")
        if b"ERROR" not in response:
            with open(f"downloaded_{filename}", "wb") as f:
                f.write(response)
            byte_count = len(response)
        else:
            return f"Failed to download {filename}", 0.0, 0.0
    elif op == "upload" and filename:
        if not os.path.exists(filename):
            return f"File not found: {filename}", 0.0, 0.0
        with open(filename, "rb") as f:
            content = f.read()
        byte_count = len(content)
        response = send_command(f"UPLOAD {filename}", content)
        if b"OK" not in response:
            return f"Failed to upload {filename}", 0.0, 0.0
    else:
        return "Invalid operation", 0.0, 0.0

    end_time = time.time()
    elapsed = end_time - start_time
    throughput = byte_count / elapsed if elapsed > 0 else 0
    return "Success", elapsed, throughput

def run_clients(mode, op, filename=None, num_clients=1):
    executor_cls = ThreadPoolExecutor if mode == "thread" else ProcessPoolExecutor
    with executor_cls(max_workers=num_clients) as executor:
        futures = [executor.submit(worker_task, op, filename) for _ in range(num_clients)]

        total_time = 0.0
        total_bytes = 0.0
        for i, future in enumerate(futures):
            status, elapsed, throughput = future.result()
            print(f"[Client-{i+1}] Status: {status} | Time: {elapsed:.4f} sec | Throughput: {throughput:.2f} B/s")
            total_time += elapsed
            total_bytes += throughput * elapsed

        print("\n=== Summary ===")
        print(f"Total clients     : {num_clients}")
        print(f"Total time (sum)  : {total_time:.4f} seconds")
        print(f"Avg time/client   : {total_time/num_clients:.4f} seconds")
        print(f"Avg throughput/client: {total_bytes/total_time:.2f} B/s")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python file_client_pool.py <mode> <operation> <num_clients> [filename]")
        print("mode: thread | process")
        print("operation: list | upload | download")
        sys.exit(1)

    mode = sys.argv[1]
    operation = sys.argv[2]
    num_clients = int(sys.argv[3])
    filename = sys.argv[4] if len(sys.argv) > 4 else None

    if mode not in ["thread", "process"]:
        print("Invalid mode. Use 'thread' or 'process'.")
        sys.exit(1)

    run_clients(mode, operation, filename, num_clients)
