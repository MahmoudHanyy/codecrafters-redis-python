import time 

class Database:
    def __init__(self):
        self.store = {}

    def set(self, key, value, expire: int = None) -> None:
        self.store[key] = (value, time.time() + expire if expire is not None else None)

    def get(self, key, default=None):
        if key not in self.store:
            return default
        value, expiry = self.store[key]
        if expiry is not None and expiry < time.time():
            del self.store[key]
            return default
        return value
    
    def rpush(self, key, value):
        if key not in self.store:
            self.store[key] = ([], None)
        lst, expiry = self.store[key]
        lst.append(value)
        self.store[key] = (lst, expiry)
        return len(lst)
    
    def lpush(self, key, value):
        if key not in self.store:
            self.store[key] = ([], None)
        lst, expiry = self.store[key]
        lst.insert(0, value)
        self.store[key] = (lst, expiry)
        return len(lst)
    
    def lrange(self, key, start, end):
        if key not in self.store:
            return []
        lst, expiry = self.store[key]
        if expiry is not None and expiry < time.time():
            del self.store[key]
            return []
        if end < 0:
            end = len(lst) + end
        return lst[start:end+1]