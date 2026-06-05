
import asyncio

class Stream:
    def __init__(self):
        self.stream = {}
        self.events = {}

    def validate_id(self, id):
        timestamp, seq = id.split(b'-')
        if not (timestamp.isdigit() and seq.isdigit()) or (timestamp == b'0' and seq == b'0'):
            raise ValueError("(error) ERR The ID specified in XADD must be greater than 0-0")
        for key in self.stream.keys():
            if timestamp <= self.stream[key].get('id', b'0-0') and seq <= self.stream[key].get('id', b'0-0'):
                raise ValueError("(error) ERR The ID specified in XADD is equal or smaller than the target stream top item")


    def xadd(self, key, id, *values):
        self.validate_id(id)
        if key not in self.stream:
            self.stream[key] = {'id': id}
        for i in range(0, len(values), 2):
            self.stream[key][values[i]] = values[i + 1]