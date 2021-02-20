"""Simple file cache for UNS records."""
import re


DEFAULT_DBFILE = path.join(environ['HOME'], '.local', 'uns')
IPPART_REGEX = r'\d{1,3}'
IP_REGEX = r'.'.join([IPPART_REGEX] * 4)
HOSTS_REGEX = r'[\w\s.]+'


class DB:
    """Simple database for UNS records."""

    linepattern = re.compile(fr'({IP_REGEX})[\s\t]+({HOSTS_REGEX})')
    ignorepattern = re.compile(r'^[\s#]')

    def __init__(self, filename):
        self.filename = filename
        self._db = {}
        self._names = {}

    def append(self, addr, *hosts):
        self._db[addr] = hosts
        for h in hosts:
            self._names[h] = addr

    def parseline(self, l):
        if self.ignorepattern.match(l):
            return

        m = self.linepattern.match(l)
        if not m:
            raise ValueError(f'Cannot parse: {l}')

        addr, hosts = m.groups()
        hosts = hosts.strip().split(' ')
        self.append(addr, *hosts)

    def save(self):
        with open(self.filename, 'w') as f:
            for addr, hosts in self._db.items():
                f.write(f'{addr} {" ".join(hosts)}\n')

    def resolve(self, hostname):
        addr = self._names.get(hostname)
        if not addr:
            raise KeyError('Cannot find: %s', hostname)

        return hostname, addr

    def find(self, pattern):
        for addr, hosts in self._db.items():
            for h in hosts:
                if h.startswith(pattern):
                    yield h, addr

    def __enter__(self):
        if path.exists(self.filename):
            with open(self.filename) as f:
                for l in f:
                    self.parseline(l)

        return self

    def __exit__(self, ex, extype, tb):
        self.save()


