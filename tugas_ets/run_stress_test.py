import subprocess
import time
import csv
import itertools
import os

MODES = ['thread', 'process']
OPERATIONS = ['upload', 'download']
VOLUME_INFO = {
    '10MB': ('file_10mb.txt', 10 * 1024 * 1024),
    '50MB': ('file_50mb.txt', 50 * 1024 * 1024),
    '100MB': ('file_100mb.txt', 100 * 1024 * 1024)
}
CLIENT_WORKERS = [1, 5, 50]
SERVER_WORKERS = [1, 5, 50]

SERVER_SCRIPTS = {
    'thread': 'file_server_threadpool.py',
    'process': 'file_server_processpool.py'
}

CLIENT_SCRIPT = 'file_client_pool.py'
OUTPUT_CSV = 'stress_test_results.csv'


def generate_dummy_file(filename, size_bytes):
    if not os.path.exists(filename):
        print(f"Generating {filename} ...")
        with open(filename, 'wb') as f:
            f.write(os.urandom(size_bytes))


def run_server(mode, server_workers):
    return subprocess.Popen(['python3', SERVER_SCRIPTS[mode], str(server_workers)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)


def run_client(mode, operation, client_workers, filename):
    result = subprocess.run(['python3', CLIENT_SCRIPT, mode, operation, str(client_workers), filename],
                            capture_output=True, text=True)
    return result.stdout


def parse_client_output(output):
    lines = output.strip().splitlines()
    total_time, total_throughput = 0, 0
    success, fail = 0, 0
    for line in lines:
        if '[Client-' in line:
            if 'Success' in line:
                success += 1
            else:
                fail += 1
            try:
                time_taken = float(line.split('Time: ')[1].split(' sec')[0])
                throughput = float(line.split('Throughput: ')[1].split(' B/s')[0])
                total_time += time_taken
                total_throughput += throughput
            except:
                continue
    return total_time, total_throughput, success, fail


def write_csv_header():
    if not os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'No', 'Mode', 'Operation', 'Volume', 'Client Workers', 'Server Workers',
                'Total Time', 'Avg Time/Client', 'Avg Throughput/Client', 'Success', 'Fail'
            ])


def append_result(no, mode, op, vol, c, s, total_time, avg_time, avg_throughput, success, fail):
    with open(OUTPUT_CSV, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            no, mode, op, vol, c, s,
            f"{total_time:.4f}", f"{avg_time:.4f}", f"{avg_throughput:.2f}", success, fail
        ])


def main():
    for vol, (filename, size_bytes) in VOLUME_INFO.items():
        generate_dummy_file(filename, size_bytes)

    write_csv_header()
    total_test = 0

    for mode in MODES:
        for server_worker in SERVER_WORKERS:
            print(f"\n=== Starting SERVER: mode={mode}, workers={server_worker} ===")
            server_proc = run_server(mode, server_worker)
            time.sleep(1.5)

            try:
                for operation, (vol_label, (filename, _)) in itertools.product(
                        OPERATIONS, VOLUME_INFO.items()):
                    for client_worker in CLIENT_WORKERS:
                        total_test += 1
                        print(f"\n[Test {total_test}] {mode.upper()} | {operation.upper()} | {vol_label} | "
                              f"Client={client_worker}, Server={server_worker}")

                        output = run_client(mode, operation, client_worker, filename)
                        print(output)

                        total_time, total_throughput, success, fail = parse_client_output(output)
                        avg_time = total_time / client_worker if client_worker else 0
                        avg_throughput = total_throughput / client_worker if client_worker else 0

                        append_result(total_test, mode, operation, vol_label,
                                      client_worker, server_worker,
                                      total_time, avg_time, avg_throughput, success, fail)

            finally:
                server_proc.terminate()
                try:
                    server_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_proc.kill()
                time.sleep(1)

    print(f"\n All {total_test} experiments finished. Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
