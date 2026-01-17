import threading as th
import queue

def worker(mass, number, k):
    while True:
        line = mass[number%k].get()
        if line is None:
            break
        with open(f"worker_{number}.txt", 'a') as f:
            f.write(line + '\n')

def run(file_name, k):
    mass_k_files = [queue.Queue() for _ in range(k)]

    try:
        with open(file_name, 'r') as f:
            for ind, line in enumerate(f):
                mass_k_files[ind % k].put(line.strip())
    except FileNotFoundError:
        print("NOOOO file")
        return

    for i in range(k):
        mass_k_files[i].put(None)

    threads = [th.Thread(target=worker, args=(mass_k_files, i, k)) for i in range(k)]

    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()

    print("finish")

if __name__ == "__main__":
    file_name = "urls2.txt"
    k = 2
    run(file_name, k)
        

