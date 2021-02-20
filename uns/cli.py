import easycli as cli


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
        cli.Argument('hostname', default=GRP),
        cli.Argument('-a', '--address', default=GRP, help=f'Default: {GRP}'),
        cli.Argument('-p', '--port', default=PORT, type=int,
                     help=f'Default: {PORT}'),
    ]

    def __call__(self, args):
        answer = args.hostname
        sock = createsocket()
        verb = struct.pack('>B', VERB_ANSWER)
        print(f'Answering {answer} to {args.address}:{args.port}')
        sock.sendto(verb + answer.encode(), (args.address, args.port))


class Find(cli.SubCommand):
    """Find an ip address by it's name."""

    __command__ = 'find'
    __aliases__ = ['f']
    __arguments__ = [
        cli.Argument('pattern'),
        cli.Argument('--no-cache', action='store_true'),
        cli.Argument('-s', '--short', action='store_true'),
        cli.Argument('-t', '--timeout', type=int, default=5,
                     help='Seconds wait before exit, 0: infinite, default: 5'),
    ]

    def online(self, db, args):
        sock = createsocket(args.timeout)
        discover = struct.pack('>B', VERB_DISCOVER)
        sock.sendto(discover + args.pattern.encode(), TARGET)
        try:
            while True:
                verb, name, addr, _ = readpacket(sock)
                db.append(addr, name)
                printrecord(args, name, addr, False)
        except socket.timeout:
            if not args.short:
                print(f'Timeout reached: {args.timeout}', file=sys.stderr)
                return
        except KeyboardInterrupt:
            print('Terminated by user.', file=sys.stderr)

    def __call__(self, args):
        with DB(args.dbfile) as db:
            if not args.no_cache:
                for name, addr in db.find(args.pattern):
                    printrecord(args, name, addr, True)

            self.online(db, args)


class Resolve(cli.SubCommand):
    """Resolve an ip address by it's name."""

    __command__ = 'resolve'
    __aliases__ = ['r', 'd']
    __arguments__ = [
        cli.Argument('hostname'),
        cli.Argument('--no-cache', action='store_true'),
        cli.Argument('-s', '--short', action='store_true'),
        cli.Argument('-t', '--timeout', type=int, default=0,
                     help='Wait for response, default: 0'),
    ]

    def __call__(self, args):
        with DB(args.dbfile) as db:
            if args.no_cache:
                return self.online(db, args)

            try:
                name, addr = db.resolve(args.hostname)
                printrecord(args, name, addr, True)

            except KeyError:
                return self.online(db, args)


class Sniff(cli.SubCommand):
    """Sniff IGMP packets."""

    __command__ = 'sniff'
    __aliases__ = ['s']
    __arguments__ = [
    ]

    def __call__(self, args):
        sock = createsocket()
        print(f'Listening to {GRP}:{PORT}')
        sock.bind(TARGET)
        mreq = struct.pack("4sl", socket.inet_aton(GRP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        try:
            while True:
                verb, name, addr, port = readpacket(sock)
                print(f'{addr}:{port} {name}')
        except KeyboardInterrupt:
            print('Terminated by user.', file=sys.stderr)


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
            print(__version__)
            return

        self._parser.print_help()


