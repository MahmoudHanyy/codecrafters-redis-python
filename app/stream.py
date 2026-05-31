
import asyncio

class Stream:
    def __init__(self, key):
        self.stream = {}
        self.events = {}

    def xad(self, key, id, *values):
        if key not in self.stream:
            self.stream[key] = {'id': id}
        for i in range(0, len(values), 2):
            self.stream[key][values[i]] = values[i + 1]