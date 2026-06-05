
import asyncio

class Stream:
    def __init__(self):
        self.stream = {}
        self.events = {}

    def xadd(self, key, id, *values):
        if key not in self.stream:
            self.stream[key] = {'id': id}
        for i in range(0, len(values), 2):
            self.stream[key][values[i]] = values[i + 1]