
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
            if timestamp <= current_timestamp and seq <= current_seq or timestamp < current_timestamp:
                raise ValueError(b"-ERR The ID specified in XADD is equal or smaller than the target stream top item\r\n")

    def xadd(self, key, id, *values):
        timestamp, seq = id.split(b'-')
        if seq == b'*':
            seq = b'1' if timestamp == b'0' else b'0'
            if key in self.stream and self.stream[key].get('entries'):
                last_id = self.stream[key]['entries'][-1]['id']
                last_timestamp, last_seq = last_id.split(b'-')
                if timestamp == last_timestamp:
                    seq = str(int(last_seq) + 1).encode()
        id = timestamp + b'-' + seq
        self.validate_id(key, id)
        if key not in self.stream:
            self.stream[key] = {'entries': [{'id': id, 'values': values}]}
        else:
            for i in range(0, len(values), 2):
                self.stream[key]['entries'].append({'id': id, 'values': values[i:i+2]})

        return id