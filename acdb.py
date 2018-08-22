import base64
import collections
import json
import os.path

import requests
import requests.adapters


class MemDriver:
    def __init__(self):
        self.memcache = {}

    def set(self, k, s):
        self.memcache[k] = s

    def get(self, k):
        return self.memcache[k]

    def nil(self, k):
        del self.memcache[k]


class DocDriver:
    def __init__(self, root):
        self.root = root
        os.makedirs(self.root, 0o666, exist_ok=True)

    def set(self, k, s):
        with open(os.path.join(self.root, k), 'w') as f:
            f.write(s)

    def get(self, k):
        with open(os.path.join(self.root, k), 'r') as f:
            return f.read()

    def nil(self, k):
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

    def nil(self, k):
        del self.dict[k]


class MapDriver:
    def __init__(self, root):
        self.doc_driver = DocDriver(root)
        self.lru_driver = LruDriver(1024)

    def set(self, k, s):
        self.doc_driver.set(k, s)
        self.lru_driver.set(k, s)

    def get(self, k):
        try:
            return self.lru_driver.get(k)
        except KeyError:
            pass
        s = self.doc_driver.get(k)
        self.lru_driver.set(k, s)
        return s

    def nil(self, k):
        self.doc_driver.nil(k)
        self.lru_driver.nil(k)


class JSONEmerge:
    def __init__(self, driver):
        self.driver = driver

    def get(self, k):
        s = self.driver.get(k)
        return json.loads(s)

    def set(self, k, v):
        s = json.dumps(v)
        self.driver.set(k, s)

    def nil(self, k):
        self.driver.nil(k)

    def add(self, k, n):
        s = self.driver.get(k)
        v = json.loads(s)
        v += n
        s = json.dumps(v)
        self.driver.set(k, s)

    def dec(self, k, n):
        return self.add(k, -n)


class HTTPEmerge:
    def __init__(self, server, conf):
        if not server.startswith('https://'):
            server = 'https://' + server
        self.server = server
        self.session = requests.Session()
        self.session.mount(server, requests.adapters.HTTPAdapter(max_retries=8))
        ca_crt = os.path.join(conf, 'ca.crt')
        client_crt = os.path.join(conf, 'client.crt')
        client_key = os.path.join(conf, 'client.key')
        self.session.verify = ca_crt
        self.session.cert = (client_crt, client_key)

    def get(self, k):
        j = {'command': 'GET', 'k': k}
        resp = self.session.put(self.server, json=j)
        body = resp.json()
        if body['err'] != '':
            raise Exception(body['err'])
        return json.loads(base64.b64decode(body['v'].encode()))

    def set(self, k, v):
        s = json.dumps(v)
        t = base64.b64encode(s.encode()).decode()
        j = {'command': 'SET', 'k': k, 'v': t}
        resp = self.session.put(self.server, json=j)
        body = resp.json()
        if body['err'] != '':
            raise Exception(body['err'])
        return json.loads(resp.text)

    def add(self, k, n):
        s = json.dumps(n)
        t = base64.b64encode(s.encode()).decode()
        j = {'command': 'ADD', 'k': k, 'v': t}
        resp = self.session.put(self.server, json=j)
        body = resp.json()
        if body['err'] != '':
            raise Exception(body['err'])

    def dec(self, k, n):
        s = json.dumps(n)
        t = base64.b64encode(s.encode()).decode()
        j = {'command': 'DEC', 'k': k, 'v': t}
        resp = self.session.put(self.server, json=j)
        body = resp.json()
        if body['err'] != '':
            raise Exception(body['err'])

    def nil(self, k):
        j = {'command': 'DEL', 'k': k}
        resp = self.session.put(self.server, json=j)
        body = resp.json()
        if body['err'] != '':
            raise Exception(body['err'])


def mem():
    return JSONEmerge(MemDriver())


def doc(root):
    return JSONEmerge(DocDriver(root))


def lru(size):
    return JSONEmerge(LruDriver(size))


def syn(root):
    return JSONEmerge(MapDriver(root))


def cli(server, conf):
    return HTTPEmerge(server, conf)
