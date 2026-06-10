import time
import asyncio
from stream import Stream

class Database:
    def __init__(self):
        self.store = {}
        self.events = {}

    def get_event(self, key):
        if key not in self.events:
            self.events[key] = asyncio.Event()
        return self.events[key]

    def notify(self, key):
        if key in self.events:
            self.events[key].set()

    def set(self, key, value, expire=None):
        self.store[key] = (value, time.time() + expire if expire is not None else None)

    def get(self, key, default=None):
        if key not in self.store:
            return default
        value, expiry = self.store[key]
        if expiry is not None and expiry < time.time():
            del self.store[key]
            return default
        return value

    def get_list(self, key):
        if key not in self.store:
            return []
        value, expiry = self.store[key]
        if not isinstance(value, list):
            return []
        return value

    def set_list(self, key, lst, expiry=None):
        self.store[key] = (lst, expiry)

    def rpush(self, key, value):
        if key not in self.store:
            self.store[key] = ([], None)
        lst, expiry = self.store[key]
        lst.append(value)
        self.store[key] = (lst, expiry)
        self.notify(key)
        return len(lst)

    def lpush(self, key, value):
        if key not in self.store:
            self.store[key] = ([], None)
        lst, expiry = self.store[key]
        lst.insert(0, value)
        self.store[key] = (lst, expiry)
        self.notify(key)
        return len(lst)

    def lrange(self, key, start, end):
        lst = self.get_list(key)
        if not lst:
            return []
        if end < 0:
            end = len(lst) + end
        return lst[start:end + 1]

    def lpop(self, key):
        lst = self.get_list(key)
        if not lst:
            return None
        value = lst.pop(0)
        self.store[key] = (lst, self.store[key][1])
        return value
    
    def get_stream(self, key, create=False):
        """Return the Stream stored at key, creating one if asked.
        Returns None if the key holds a non-stream value (WRONGTYPE)."""
        existing = self.get(key)
        if isinstance(existing, Stream):
            return existing
        if existing is not None:
            return None
        if create:
            s = Stream()
            self.store[key] = (s, None)
            return s
        return None

    def type(self, key):
        value = self.get(key)
        if value is None:
            return "none"
        if isinstance(value, Stream):
            return "stream"
        if isinstance(value, list):
            return "list"
        if isinstance(value, dict):
            return "hash"
        if isinstance(value, set):
            return "set"
        return "string"