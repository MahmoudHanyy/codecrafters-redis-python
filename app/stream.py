
import asyncio

class Stream:
    def __init__(self):
        self.stream = {}
        self.events = {}

    def validate_id(self, key, id):
        if key not in self.stream:
            return
        timestamp, seq = id.split(b'-')
        if not (timestamp.isdigit() and seq.isdigit()) or (timestamp == b'0' and seq == b'0'):
            raise ValueError(b"-ERR The ID specified in XADD must be greater than 0-0\r\n")
        for entry in self.stream[key].get('entries', []):
            current_timestamp, current_seq = entry['id'].split(b'-')
            if timestamp <= current_timestamp and seq <= current_seq:
                raise ValueError(b"-ERR The ID specified in XADD is equal or smaller than the target stream top item\r\n")

    def xadd(self, key, id, *values):
        self.validate_id(key, id)
        if key not in self.stream:
            self.stream[key] = {'entries': [{'id': id, 'values': values}]}
        else:
            for i in range(0, len(values), 2):
                self.stream[key]['entries'].append({'id': id, 'values': values[i:i+2]})