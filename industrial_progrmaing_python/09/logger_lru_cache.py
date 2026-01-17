# pylint: disable=duplicate-code
import logging
import sys


def create_logger(sys_args):

    name = "cache"
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(f"{name}.log", mode="w")

    if "-s" in sys_args:
        stream_handler = logging.StreamHandler()
        log.addHandler(stream_handler)
    elif "-f" in sys_args:
        fmt = logging.Formatter(
            "FILE %(asctime)s\t%(levelname)s\t%(name)s\t%(message)s"
        )
        file_handler.setFormatter(fmt)
    elif "-fs" in sys_args or "-sf" in sys_args:
        stream_handler = logging.StreamHandler()

        fmt1 = logging.Formatter(
            "FILE %(asctime)s\t%(levelname)s\t%(name)s\t%(message)s"
        )
        fmt2 = logging.Formatter(
            "STREAM %(asctime)s\t%(levelname)s\t%(name)s\t%(message)s"
        )

        file_handler.setFormatter(fmt1)
        stream_handler.setFormatter(fmt2)
        log.addHandler(stream_handler)

    log.addHandler(file_handler)

    return log


class Noda:  # pylint: disable=too-few-public-methods
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, limit, log=None):
        self.limit = limit
        self.cache = {}
        self.head = Noda()
        self.tail = Noda()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.logger = log

    def add(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def remove(self, node):
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def to_head(self, node):
        self.remove(node)
        self.add(node)

    def delete_tail(self):
        node = self.tail.prev
        self.remove(node)
        return node

    def get(self, key):
        if key not in self.cache:
            if self.logger:
                self.logger.info("Cache not have a key: %s", key)
            return None

        node = self.cache[key]
        self.to_head(node)

        if self.logger:
            current = self.head.next
            current_mass = []
            while current != self.tail:
                current_mass.append((current.key, current.value))
                current = current.next
            self.logger.info(
                "Cache get key:%s, cache:%s, return: %s",
                key, current_mass, node.value
            )
        return node.value

    def set(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self.to_head(node)

            if self.logger:
                current = self.head.next
                current_mass = []
                while current != self.tail:
                    current_mass.append((current.key, current.value))
                    current = current.next
                self.logger.info(
                    "Cache put exist key:%s, value:%s, cache:%s",
                    key, value, current_mass
                )
        else:
            node = Noda(key, value)
            self.cache[key] = node
            self.add(node)
            if len(self.cache) > self.limit:
                tail = self.delete_tail()
                self.cache.pop(tail.key)

            if self.logger:
                current = self.head.next
                current_mass = []
                while current != self.tail:
                    current_mass.append((current.key, current.value))
                    current = current.next
                self.logger.info(
                    "Cache put new key:%s, value:%s, cache:%s",
                    key, value, current_mass
                )

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)


if __name__ == "__main__":
    logger = create_logger(sys.argv)
    cache = LRUCache(2, logger)
    cache.set("k1", "v1")
    cache.set("k2", "v2")
    cache.get("k1")
    cache.set("k3", "v3")
    cache.set("k2", "v5")
    cache.get("k2")
