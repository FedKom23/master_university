import sys
import socket
import threading
import queue


class Client:
    def __init__(self, host, port):
        self.num_threads, self.filename = self.get_info()
        self.host = host
        self.port = port
        self.urls = queue.Queue()
        self.worker_threads = []
        self.lock = threading.Lock()

    def get_info(self):
        if len(sys.argv) != 3:
            sys.exit(1)

        num_threads = int(sys.argv[1])
        filename = sys.argv[2]
        return num_threads, filename

    def worker(self):
        while True:
            try:
                url = self.urls.get_nowait()
            except queue.Empty:
                break

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.port))
                    s.sendall(url)
                    response = s.recv(4096)
                    s.close()
                    with self.lock:
                        print(f"URL: {url}\nResponse: {response}\n")
            except OSError as e:
                with self.lock:
                    print(f"Error processing {url}: {e}")

    def start_workers(self):
        for i in range(self.num_threads):
            thread = threading.Thread(
                target=self.worker, name=f"Client-{i}", daemon=True
            )
            thread.start()
            self.worker_threads.append(thread)

    def run(self):
        with open(self.filename, 'r', encoding='utf-8') as file:
            for line in file:
                url = line.strip()
                if url:
                    self.urls.put(url)

        self.start_workers()
        for thread in self.worker_threads:
            thread.join()
