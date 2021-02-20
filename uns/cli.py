import sys
import socket
from os import path, environ

import easycli as cli

from .constants import IGMP_PORT, IGMP_ADDRESS, VERBS
from . import protocol, cache


DEFAULT_DBFILE = path.join(environ['HOME'], '.local', 'uns')


def printrecord(name, addr, cache, short=False):
    if short:
        print(addr)
        return

    flags = ' [cache]' if cache else ''
    print(f'{addr} {name}{flags}')


class Answer(cli.SubCommand):
    """Answer command line interface."""

    __command__ = 'answer'
    __aliases__ = ['a', 'ans']
    __arguments__ = [
        cli.Argument('hostname', default=IGMP_ADDRESS),
        cli.Argument(
            '-a', '--address',
            default=IGMP_ADDRESS,
            help=f'Default: {IGMP_ADDRESS}'
        ),
        cli.Argument(
            '-p', '--port',
            default=IGMP_PORT,
            type=int,
            help=f'Default: {IGMP_PORT}'
        ),
    ]

#    def __call__(self, args):
#        answer = args.hostname
#        sock = createsocket()
#        verb = struct.pack('>B', VERB_ANSWER)
#        print(f'Answering {answer} to {args.address}:{args.port}')
#        sock.sendto(verb + answer.encode(), (args.address, args.port))


class Sniff(cli.SubCommand):
    """Sniff IGMP packets."""

    __command__ = 'sniff'
    __aliases__ = ['s']
    __arguments__ = [
    ]

    def __call__(self, args):
        print(f'Listening to {IGMP_ADDRESS}:{IGMP_PORT}')
        try:
            for verb, name, addr, port in protocol.sniff():
                print(f'{addr}:{port} {VERBS.get(verb)}{name}')
        except KeyboardInterrupt:
            print('Terminated by user.', file=sys.stderr)
            return 3


class Find(cli.SubCommand):
    """Find an ip address by it's name."""

    __command__ = 'find'
    __aliases__ = ['f']
    __arguments__ = [
        cli.Argument('pattern'),
        cli.Argument('--nocache', action='store_true'),
        cli.Argument('-s', '--short', action='store_true'),
        cli.Argument('-t', '--timeout', type=int, default=5,
                     help='Seconds wait before exit, 0: infinite, default: 5'),
    ]

    def __call__(self, args):
        if not args.nocache:
            with cache.DB(args.dbfile) as db:
                for name, addr in db.find(args.pattern):
                    printrecord(name, addr, True, short=args.short)

        # Searching network
        try:
            for n, a in protocol.find(args.pattern, timeout=args.timeout):
                printrecord(n, a, False, short=args.short)
        except socket.timeout:
            if not args.short:
                print(f'Timeout reached: {args.timeout}.', file=sys.stderr)
            return 2

        except KeyboardInterrupt:
            if not args.short:
                print('Terminated by user.', file=sys.stderr)
            return 3


class Resolve(cli.SubCommand):
    """Resolve an ip address by it's name."""

    __command__ = 'resolve'
    __aliases__ = ['r', 'd']
    __arguments__ = [
        cli.Argument('hostname'),
        cli.Argument('--nocache', action='store_true'),
        cli.Argument('-s', '--short', action='store_true'),
        cli.Argument('-t', '--timeout', type=int, default=0,
                     help='Wait for response, default: 0'),
    ]

    def __call__(self, args):
        resolve = protocol.resolve

        if not args.nocache:
            with cache.DB(args.dbfile) as cache_:
                resolve = cache_(resolve)
                name, addr, fromcache = \
                    resolve(args.hostname, timeout=args.timeout)
                printrecord(name, addr, fromcache, short=args.short)
                return

        # Searching network
        try:
            name, addr = resolve(args.hostname, timeout=args.timeout)
        except socket.timeout:
            if not args.short:
                print(f'Timeout reached: {args.timeout}.', file=sys.stderr)
            return 2

        except KeyboardInterrupt:
            if not args.short:
                print('Terminated by user.', file=sys.stderr)
            return 3
        else:
            printrecord(name, addr, False, short=args.short)


class UNS(cli.Root):
    """UNS root command line handler."""

    __completion__ = True
    __help__ = 'UNS utility.'
    __arguments__ = [
        cli.Argument('-v', '--version', action='store_true'),
        cli.Argument(
            '--dbfile',
            default=DEFAULT_DBFILE,
            help=f'Database file, default: {DEFAULT_DBFILE}'
        ),
        Resolve,
        Answer,
        Sniff,
        Find,
    ]

    def __call__(self, args):
        if args.version:
            import uns
            print(uns.__version__)
            return

        self._parser.print_help()
