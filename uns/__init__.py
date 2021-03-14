"""UNS.

Simple IGMP discovery protocol
"""
from . import protocol, cache
from .constants import DEFAULT_DBFILE


__version__ = '2.0.0'


def resolve(hostname, timeout=0, force=False, noresolve=False,
            dbfile=DEFAULT_DBFILE):
    assert not (force and noresolve)

    with cache.DB(dbfile) as db:
        if force:
            db.invalidate(hostname)

        return db.getaddr(
            hostname,
            resolve=not noresolve,
            resolvetimeout=timeout
        )
