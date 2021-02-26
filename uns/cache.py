"""Simple file cache for UNS records."""
from . import protocol


class InvalidDBFileError(Exception):
    pass


class HostNotFoundError(Exception):
    pass


class DB:
    """Simple database for UNS records."""

    def __init__(self, filename):
        self.filename = filename
        self._db = {}
        self._names = {}
        self._dirty = False
        self.load()

    def set(self, addr, hostname, dirty=True):
        self._db[addr] = hostname
        self._names[hostname] = addr
        self._dirty = dirty

    def _parseline(self, l):
        try:
            addr, hostname = l.strip().split(' ')
            self.set(addr, hostname, False)
        except ValueError:
            raise InvalidDBFileError(self.filename)

    def save(self):
        with open(self.filename, 'w') as f:
            for addr, hosts in self._db.items():
                f.write(f'{addr} {hosts}\n')

    def getaddr(self, hostname, resolve=True, resolvetimeout=None):
        addr = self._names.get(hostname)
        if addr:
            return addr, True

        if resolve:
            addr = protocol.resolve(hostname, resolvetimeout)
            self.set(addr, hostname, True)
            return addr, False

        raise HostNotFoundError(hostname)

    def invalidate(self, hostname):
        addr = self._names.get(hostname)
        if not addr:
            return

        del self._names[hostname]
        del self._db[addr]

    def find(self, pattern):
        for addr, host in self._db.items():
            if host.startswith(pattern):
                yield host, addr

    def load(self):
        try:
            with open(self.filename) as f:
                for l in f:
                    self._parseline(l)
        except FileNotFoundError:  # pragma: no cover
            # Don't worry! the file will be created when save() method is
            # called.
            pass

    def __enter__(self):
        return self

    def __exit__(self, ex, extype, tb):
        if self._dirty:
            self.save()
