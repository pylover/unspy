import sys
import functools
from unittest import mock

import pytest

from uns.cli import UNS


@pytest.fixture
def dbfile_mock():
    dbfile = mock.mock_open(read_data='10.0.0.3 bar.com\n')
    with mock.patch('uns.cache.open', dbfile) as m:
        yield m


@pytest.fixture
def badfile_mock():
    dbfile = mock.mock_open(read_data='Malformed\n')
    with mock.patch('uns.cache.open', dbfile) as m:
        yield m


@pytest.fixture
def socketclass_mock():
    with mock.patch('socket.socket') as m:
        s = m.return_value
        s.recvfrom.return_value = b'\x02foo.com', ('10.0.0.2', 5333)
        yield m


@pytest.fixture
def requests_mock():
    with mock.patch('requests.request') as m:
        response = m.return_value
        response.text = 'bar'
        response.status_code = 200
        yield m


@pytest.fixture
def cliapp(capsys):

    def wrapper(*args):
        prog = sys.argv[0]
        sys.argv[0] = 'uns'
        try:
            status = UNS.quickstart(argv=args)
        except:  # noqa
            status = 1
            err = sys.exc_info()[1]
            print(err, file=sys.stderr)
        stdout, stderr = capsys.readouterr()
        sys.argv[0] = prog
        return status, stdout, stderr

    return wrapper


@pytest.fixture
def answercli(cliapp):
    return functools.partial(cliapp, 'answer')


@pytest.fixture
def resolvecli(cliapp):
    return functools.partial(cliapp, 'resolve')


@pytest.fixture
def sniffcli(cliapp):
    return functools.partial(cliapp, 'sniff')


@pytest.fixture
def findcli(cliapp):
    return functools.partial(cliapp, 'find')


@pytest.fixture
def httpcli(cliapp):
    return functools.partial(cliapp, 'http')
