import asyncio
import time


class Stream:
    type = "stream"

    def __init__(self):
        self.entries = []

    def xadd(self, id, *values):
        fields = {}
        for i in range(0, len(values), 2):
            fields[values[i]] = values[i + 1]
        self.entries.append((id, fields))
        return id

class RedisList:
    type = "list"

    def __init__(self):
        self.data = []


class Database:
    def __init__(self):
        self.store = {}   # key -> {"type": ..., "value": ..., "expiry": ...}
        self.events = {}

    # --- internal helpers ---

    def _is_expired(self, key):
        expiry = self.store[key]["expiry"]
        if expiry is not None and expiry < time.time():
            del self.store[key]
            return True
        return False

    def _get_entry(self, key):
        if key not in self.store:
            return None
        if self._is_expired(key):
            return None
        return self.store[key]

    # --- events ---

    def get_event(self, key):
        if key not in self.events:
            self.events[key] = asyncio.Event()
        return self.events[key]

    def notify(self, key):
        if key in self.events:
            self.events[key].set()

    # --- string ---

    def set(self, key, value, expire=None):
        self.store[key] = {
            "type": "string",
            "value": value,
            "expiry": time.time() + expire if expire is not None else None,
        }

    def get(self, key, default=None):
        entry = self._get_entry(key)
        if entry is None or entry["type"] != "string":
            return default
        return entry["value"]

    # --- list ---

    def _get_or_create_list(self, key):
        entry = self._get_entry(key)
        if entry is None:
            self.store[key] = {"type": "list", "value": [], "expiry": None}
        elif entry["type"] != "list":
            raise TypeError(f"Key '{key}' holds a {entry['type']}, not a list")
        return self.store[key]["value"]

    def rpush(self, key, value):
        lst = self._get_or_create_list(key)
        lst.append(value)
        self.notify(key)
        return len(lst)

    def lpush(self, key, value):
        lst = self._get_or_create_list(key)
        lst.insert(0, value)
        self.notify(key)
        return len(lst)

    def lrange(self, key, start, end):
        entry = self._get_entry(key)
        if entry is None or entry["type"] != "list":
            return []
        lst = entry["value"]
        if end < 0:
            end = len(lst) + end
        return lst[start:end + 1]

    def lpop(self, key):
        entry = self._get_entry(key)
        if entry is None or entry["type"] != "list":
            return None
        lst = entry["value"]
        return lst.pop(0) if lst else None

    # --- stream ---

    def _get_or_create_stream(self, key):
        entry = self._get_entry(key)
        if entry is None:
            stream = Stream()
            self.store[key] = {"type": "stream", "value": stream, "expiry": None}
        elif entry["type"] != "stream":
            raise TypeError(f"Key '{key}' holds a {entry['type']}, not a stream")
        return self.store[key]["value"]

    def xadd(self, key, id, *values):
        stream = self._get_or_create_stream(key)
        self.notify(key)
        return stream.xadd(id, *values)

    def xrange(self, key, start="-", end="+"):
        entry = self._get_entry(key)
        if entry is None or entry["type"] != "stream":
            return []
        return entry["value"].xrange(start, end)

    # --- type ---

    def type(self, key):
        entry = self._get_entry(key)
        if entry is None:
            return "none"
        return entry["type"]