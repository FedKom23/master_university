class Noda:  # pylint: disable=too-few-public-methods
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, limit):
        self.limit = limit
        self.cache = {}
        self.head = Noda()
        self.tail = Noda()
        self.head.next = self.tail
        self.tail.prev = self.head

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
            return None

        node = self.cache[key]
        self.to_head(node)
        return node.value

    def set(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self.to_head(node)
        else:
            node = Noda(key, value)
            self.cache[key] = node
            self.add(node)
            if len(self.cache) > self.limit:
                tail = self.delete_tail()
                self.cache.pop(tail.key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)
