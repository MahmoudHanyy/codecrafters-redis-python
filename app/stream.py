import time


class Stream:
    """One stream's data. Lives as a value inside the Database keyspace,
    exactly like a string or list value would."""

    def __init__(self):
        self.entries = []        # list of {'id': (ms, seq), 'fields': [bytes, ...]}
        self.last_id = (0, 0)    # O(1) validation / auto-seq cache

    def _resolve_id(self, id):
        """Turn an incoming id (b'*', b'<ms>-*', or b'<ms>-<seq>') into a
        concrete (ms, seq) tuple, generating parts as needed."""
        if id == b'*':
            ms = int(time.time() * 1000)
            seq = None
        else:
            ms_b, seq_b = id.split(b'-')
            ms = int(ms_b)
            seq = None if seq_b == b'*' else int(seq_b)

        if seq is None:
            if ms == self.last_id[0]:
                seq = self.last_id[1] + 1
            else:
                seq = 1 if ms == 0 else 0
        return (ms, seq)

    def _validate(self, new_id):
        if new_id == (0, 0):
            raise ValueError(b"-ERR The ID specified in XADD must be greater than 0-0\r\n")
        if new_id <= self.last_id:
            raise ValueError(b"-ERR The ID specified in XADD is equal or smaller than the target stream top item\r\n")

    def add(self, id, fields):
        new_id = self._resolve_id(id)
        self._validate(new_id)
        self.entries.append({'id': new_id, 'fields': list(fields)})
        self.last_id = new_id
        return b'%d-%d' % new_id
