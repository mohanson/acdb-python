# Package acdb

Package acdb manages objects between memory and file system.

```sh
$ pip install acdb
```

# Mem

MemDriver cares to store data on memory, this means that MemDriver is fast. Since there is no expiration mechanism, be careful that it might eats up all your memory.

```py
db = acdb.mem()
db.set('name', 'acdb')
assert db.get('name') == 'acdb'
```

# Doc

DocDriver use the OS's file system to manage data. In general, any high frequency operation is not recommended unless you have an enough reason.

```py
db = acdb.doc("/tmp/dat")
```

# Lru

In computing, cache algorithms (also frequently called cache replacement algorithms or cache replacement policies) are optimizing instructions, or algorithms, that a computer program or a hardware-maintained structure can utilize in order to manage a cache of information stored on the computer.

Caching improves performance by keeping recent or often-used data items in a memory locations that are faster or computationally cheaper to access than normal memory stores. When the cache is full, the algorithm must choose which items to discard to make room for the new ones.

Least recently used (LRU), discards the least recently used items first. It has a fixed size(for limit memory usages) and O(1) time lookup.

```py
db = acdb.lru(1024)
```

# Syn

MapDriver is based on DocDriver and use LruDriver to provide caching at its interface layer. The size of LruDriver is always 1024.

```py
db = acdb.syn("/tmp/dat")
```

# Licences

MIT
