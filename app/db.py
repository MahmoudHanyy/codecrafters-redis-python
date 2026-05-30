import time 

class Database:
    def __init__(self):
        self.store = {}

    def set(self, key, value, expire: int = None) -> None:
        self.store[key] = (value, time.time() + expire if expire is not None else None)
        print(f"SET {key} = {value} (expires in {expire} seconds)" if expire else f"SET {key} = {value}")

    def get(self, key, default=None):
        if key not in self.store:
            return default
        value, expiry = self.store[key]
        if expiry is not None and expiry < time.time():
            del self.store[key]
            return default
        return value