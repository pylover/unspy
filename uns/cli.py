import sys
import socket

import easycli as cli

from .constants import IGMP_PORT, IGMP_ADDRESS, VERBS, DEFAULT_DBFILE
from . import protocol, cache


short_arg = cli.Argument('-s', '--short', action='store_true')
timeout_arg = cli.Argument(
    '-t', '--timeout',
    type=int,
    default=5,
    help='Seconds wait before exit, 0: infinite, default: 5'
)


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

    def __call__(self, args):
        print(f'Answering {args.hostname} to {args.address}:{args.port}')
        protocol.answer(args.hostname, address=args.address, port=args.port)


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
                print(f'{addr}:{port} {VERBS.get(verb)} {name}')
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
        short_arg,
        timeout_arg,
    ]

    def __call__(self, args):
        if not args.nocache:
            with cache.DB(args.dbfile) as db:
                for name, addr in db.find(args.pattern):
                    printrecord(name, addr, True, short=args.short)

        # Searching network
        for n, a in protocol.find(args.pattern, timeout=args.timeout):
            printrecord(n, a, False, short=args.short)


class Resolve(cli.SubCommand):
    """Resolve an ip address by it's name."""

    __command__ = 'resolve'
    __aliases__ = ['r', 'd']
    __arguments__ = [
        cli.Argument('hostname'),
        cli.Argument(
            '--noresolve',
            action='store_true',
            help='Do not resolve the name over network.'
        ),
        short_arg,
        timeout_arg,
    ]

    def __call__(self, args):
        with cache.DB(args.dbfile) as db:
            addr, cached = db.getaddr(
                args.hostname,
                resolve=not args.noresolve,
                resolvetimeout=args.timeout,
            )
            printrecord(args.hostname, addr, cached, short=args.short)


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

    def main(self, *a, **k):
        try:
            return super().main(*a, **k)
        except socket.timeout:
            print('Timeout reached.', file=sys.stderr)
            return 2

        except KeyboardInterrupt:
            print('Terminated by user.', file=sys.stderr)
            return 3

        except cache.InvalidDBFileError as ex:
            print(f'Invalid input file: {ex}', file=sys.stderr)
            return 4

        except cache.HostNotFoundError as ex:
            print(f'Cannot find: {ex}.', file=sys.stderr)
            return 5

    def __call__(self, args):
        if args.version:
            import uns
            print(uns.__version__)
            return

        self._parser.print_help()
