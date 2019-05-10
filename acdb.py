import collections
import contextlib
import json
import os.path
import fnmatch


class MemDriver:
    def __init__(self):
        self.memcache = {}

    def set(self, k, v):
        self.memcache[k] = v

    def get(self, k):
        return self.memcache[k]

    def all(self):
        return list(self.memcache.keys())

    def rm(self, k):
        del self.memcache[k]


class DocDriver:
    def __init__(self, root):
        self.root = root
        if not os.path.exists(self.root):
            os.makedirs(self.root)

    def set(self, k, v):
        with open(os.path.join(self.root, k), 'wb') as f:
            f.write(v)

    def get(self, k):
        with open(os.path.join(self.root, k), 'rb') as f:
            return f.read()

    def all(self):
        return [e.name for e in os.scandir(self.root)]

    def rm(self, k):
        os.remove(os.path.join(self.root, k))


class LruDriver:
    def __init__(self, size=1024):
        self.size = size
        self.dict = collections.OrderedDict()

    def set(self, k, s):
        if len(self.dict) >= self.size:
            for _ in range(self.size // 4):
                self.dict.popitem(last=False)
        self.dict[k] = s

    def get(self, k):
        s = self.dict.pop(k)
        self.dict[k] = s
        return s

    def all(self):
        return list(self.dict.keys())

    def rm(self, k):
        del self.dict[k]


class MapDriver:
    def __init__(self, root):
        self.doc_driver = DocDriver(root)
        self.lru_driver = LruDriver(1024)

    def set(self, k, s):
        self.doc_driver.set(k, s)
        self.lru_driver.set(k, s)

    def get(self, k):
        with contextlib.suppress(KeyError):
            return self.lru_driver.get(k)
        s = self.doc_driver.get(k)
        self.lru_driver.set(k, s)
        return s

    def all(self):
        return self.doc_driver.all()

    def rm(self, k):
        self.doc_driver.rm(k)
        self.lru_driver.rm(k)


class Emerge:
    def __init__(self, driver):
        self.driver = driver

    def get(self, k):
        # Get gets and returns the bytes or any error encountered.
        s = self.driver.get(k)
        return json.loads(s)

    def set(self, k, v):
        # Set sets bytes with given k.
        s = json.dumps(v).encode()
        self.driver.set(k, s)

    def all(self, p='*'):
        # All returns all keys. Supported glob-style patterns.
        #
        # Supported glob-style patterns:
        #     h?llo matches hello, hallo and hxllo
        #     h*llo matches hllo and heeeello
        #     h[ae]llo matches hello and hallo, but not hillo
        #     h[^e]llo matches hallo, hbllo, ... but not hello
        #     h[a-b]llo matches hallo and hbllo

        return [e for e in self.driver.all() if fnmatch.fnmatch(e, p)]

    def rm(self, k):
        # Rm dels bytes with given k.
        self.driver.rm(k)

    def incr_by(self, k, n):
        # IncrBy increments the number stored at key by n.
        self.set(k, self.get(k) + n)

    def incr(self, k):
        # Incr increments the number stored at key by one.
        self.incr_by(k, 1)

    def decr_by(self, k, n):
        # DecrBy decrements the number stored at key by n.
        return self.incr_by(k, -n)

    def decr(self, k):
        # Decr decrements the number stored at key by one.
        return self.decr_by(k, 1)

    def some(self, k):
        # Some returns true if the key is some.
        with contextlib.suppress(Exception):
            self.get(k)
            return True
        return False

    def none(self, k):
        # None returns true if the key is none.
        with contextlib.suppress(Exception):
            self.get(k)
            return False
        return True

    def set_some(self, k, v):
        # Set key to hold value if the key is some.
        if self.some(k):
            self.set(k, v)

    def set_none(self, k, v):
        # Set key to hold value if the key is none.
        if self.none(k):
            self.set(k, v)


def mem():
    # Returns a Client with MemDriver.
    return Emerge(MemDriver())


def doc(root):
    # Returns a Client with DocDriver.
    return Emerge(DocDriver(root))


def lru(size):
    # Returns a Client with LruDriver.
    return Emerge(LruDriver(size))


def syn(root):
    # Returns a Client with MapDriver.
    return Emerge(MapDriver(root))
