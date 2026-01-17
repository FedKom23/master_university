import queue
import socket
import threading
import json
from urllib.request import urlopen
import sys


class TCPServer:  # pylint: disable=too-many-instance-attributes
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.queue = queue.Queue()
        self.num_threads, self.k = self.get_info()
        self.worker_threads = []
        self.processed = 0
        self.lock = threading.Lock()

    def get_info(self):
        if len(sys.argv) != 5:
            print(sys.argv)
            sys.exit(1)

        num_threads = int(sys.argv[2])
        k = int(sys.argv[4])
        return num_threads, k

    def check_url(self, url):
        return url.startswith("http://") or url.startswith("https://")

    def get_top_k_words(self, text, k):
        words = text.split()
        counts = {}
        for w in words:
            counts[w] = counts.get(w, 0) + 1
        sorted_words = sorted(
            counts.items(), key=lambda x: x[1], reverse=True
        )
        return dict(sorted_words[:k])

    def worker_process_url(self, conn, url):
        try:
            if not self.check_url(url):
                conn.sendall(json.dumps({"error": "Invalid URL"}).encode())
                return

            with urlopen(url, timeout=50) as response:
                text = response.read().decode('utf-8', errors='ignore')
                top_words = self.get_top_k_words(text, self.k)
                conn.sendall(json.dumps(top_words).encode())

            with self.lock:
                self.processed += 1
                print(f"[INFO] Processed {self.processed} URLs")
        except OSError as e:
            conn.sendall(json.dumps({"error": str(e)}).encode())
        finally:
            conn.close()

    def worker(self):
        while True:
            item = self.queue.get()
            if item is None:
                break

            conn, url = item
            self.worker_process_url(conn, url.decode('utf-8'))

    def start_workers(self):
        for i in range(self.num_threads):
            thread = threading.Thread(
                target=self.worker, name=f"Worker-{i}", daemon=True
            )
            thread.start()
            self.worker_threads.append(thread)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(5)
        self.start_workers()

        try:
            while True:
                try:
                    conn, _ = sock.accept()
                    data = conn.recv(1024).strip()
                    if data.lower() == b'':
                        for _ in range(self.num_threads):
                            self.queue.put(None)
                        for thread in self.worker_threads:
                            thread.join()
                        break
                    self.queue.put((conn, data))
                except socket.error:
                    break
        finally:
            sock.close()
            print("[SERVER] Shutdown complete.")
