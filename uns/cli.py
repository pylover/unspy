import sys
import socket
import functools

import easycli as cli

from .constants import IGMP_PORT, IGMP_ADDRESS, VERBS, DEFAULT_DBFILE, \
    DEFAULT_TIMEOUT
from . import protocol, cache, resolve, http


hostname_arg = functools.partial(cli.Argument, 'hostname')
nocache_arg = functools.partial(cli.Argument, '--nocache', action='store_true')
address_arg = functools.partial(cli.Argument, '-a', '--address')
port_arg = functools.partial(cli.Argument, '-p', '--port', type=int)
short_arg = functools.partial(
    cli.Argument,
    '-s',
    '--short',
    action='store_true'
)
timeout_arg = functools.partial(
    cli.Argument,
    '-t',
    '--timeout',
    type=int,
    default=DEFAULT_TIMEOUT,
    help=f'Seconds wait before exit, 0: infinite, default: {DEFAULT_TIMEOUT}'
)
noresolve_arg = functools.partial(
    cli.Argument,
    '--noresolve',
    action='store_true',
    help='Do not resolve the name over network.'
)
forceresolve_arg = functools.partial(
    cli.Argument,
    '-f', '--forceresolve',
    action='store_true',
    help='Force to resolve the name over network and update cache.'
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
        hostname_arg(default=IGMP_ADDRESS),
        address_arg(default=IGMP_ADDRESS, help=f'Default: {IGMP_PORT}'),
        port_arg(default=IGMP_PORT, help=f'Default: {IGMP_ADDRESS}'),
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
        nocache_arg(),
        short_arg(),
        timeout_arg(),
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
        hostname_arg(),
        cli.Mutex(
            noresolve_arg(),
            forceresolve_arg(),
        ),
        short_arg(),
        timeout_arg(),
    ]

    def __call__(self, args):
        addr, cached = resolve(
            args.hostname,
            args.timeout,
            args.forceresolve,
            args.noresolve,
            args.dbfile
        )
        printrecord(args.hostname, addr, cached, short=args.short)


class HTTP(cli.SubCommand):
    """Send HTTP request to a UNS host."""

    __command__ = 'http'
    __aliases__ = ['h']
    __arguments__ = [
        cli.Mutex(
            noresolve_arg(),
            forceresolve_arg(),
        ),
        timeout_arg(),
        port_arg(),
        cli.Argument('verb'),
        cli.Argument('url'),
        cli.Argument(
            'fields',
            metavar='[?]NAME=VALUE',
            default=[],
            nargs='*'
        )

    ]

    def __call__(self, args):
        fields = []
        query = []
        files = []
        body = ''
        path_ = ''
        port = ''

        urlparts = args.url.split('/')
        addr, _ = resolve(
            urlparts[0],
            args.timeout,
            args.forceresolve,
            args.noresolve,
            args.dbfile
        )
        if len(urlparts) > 1:
            path_ = '/' + '/'.join(urlparts[1:])

        if args.port:
            port = f':{args.port}'

        # Fields
        for f in args.fields:
            if '=' not in f:
                body = ' '.join(args.fields)
                break

            k, v = f.split('=')
            if k[0] == '?':
                query.append((k[1:], v))
            elif k[0] == '@':
                files.append((k[1:], v))
            else:
                fields.append((k, v))

        response = http.request(
            args.verb.upper(),
            f'http://{addr}{port}{path_}',
            query=query,
            form=body if body else fields,
            files=files,
        )

        f = sys.stderr if response.status_code >= 400 else sys.stdout
        print(response.text, end='', file=f)


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
        HTTP,
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
