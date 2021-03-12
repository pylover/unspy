import io
import sys
import traceback
import functools
from unittest import mock

import pytest

from uns import cli


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
        response.reason = 'OK'
        response.headers = {
            'content-type': 'text/plain',
            'Content-Length': '3'
        }
        raw = response.raw
        raw.version = 11
        yield m


def _cliapp(binary_output=False):

    def wrapper(*args):
        prog = sys.argv[0]

        # Override program name
        sys.argv[0] = 'uns'

        # Preserve standard files and monkeypatch them
        outback = cli.stdout
        errback = cli.stderr

        cli.stderr = io.StringIO()
        if binary_output:
            cli.stdout = mock.Mock()
            cli.stdout.buffer = io.BytesIO()
        else:
            cli.stdout = io.StringIO()

        # Run Application
        try:
            status = cli.UNS.quickstart(argv=args)
        except:  # noqa
            status = 1
            traceback.print_exc()

        # Capture files content
        stderr = cli.stderr.getvalue()
        if binary_output:
            stdout = cli.stdout.buffer.getvalue()
        else:
            stdout = cli.stdout.getvalue()

        # Restore preserved values
        sys.argv[0] = prog
        cli.stdout, cli.stderr = outback, errback

        return status, stdout, stderr

    return wrapper


@pytest.fixture
def cliapp():
    return _cliapp()


@pytest.fixture
def cliapp_binary():
    return _cliapp(binary_output=True)


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


@pytest.fixture
def httpcli_binary(cliapp_binary):
    return functools.partial(cliapp_binary, 'http')
