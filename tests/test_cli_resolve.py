import socket
from unittest import mock


def test_cli_resolve_cache(socketclass_mock, dbfile_mock, resolvecli):
    s, o, e = resolvecli('bar.com')
    assert e == ''
    assert s == 0
    assert o == '10.0.0.3 bar.com [cache]\n'
    socketclass_mock.assert_not_called()
    sock = socketclass_mock.return_value
    sock.settimeout.assert_not_called()
    sock.sendto.assert_not_called()
    sock.recvfrom.assert_not_called()
    dbfile_mock.return_value.write.assert_not_called()

    # Short result
    s, o, e = resolvecli('bar.com', '--short')
    assert e == ''
    assert s == 0
    assert o == '10.0.0.3\n'

    # Not found!
    s, o, e = resolvecli('not.found', '--noresolve')
    assert e == 'Cannot find: not.found.\n'
    assert s == 5
    assert o == ''

    # Only found in network
    socketclass_mock.reset_mock()
    s, o, e = resolvecli('foo.com')
    assert e == ''
    assert o == '10.0.0.2 foo.com\n'
    assert s == 0
    socketclass_mock.assert_called_once()
    sock = socketclass_mock.return_value
    sock.settimeout.assert_called_once()
    sock.sendto.assert_called_once_with(b'\x01foo.com', mock.ANY)
    sock.recvfrom.assert_called_once()
    dbfile_mock.return_value.write.assert_has_calls([
        mock.call('10.0.0.3 bar.com\n'),
        mock.call('10.0.0.2 foo.com\n'),
    ])

    # Invalidate, force resolve
    dbfile_mock.reset_mock()
    socketclass_mock.reset_mock()
    sock = socketclass_mock.return_value
    sock.recvfrom.return_value = b'\x02bar.com', ('10.0.0.9', 5333)
    s, o, e = resolvecli('bar.com', '--forceresolve')
    assert e == ''
    assert s == 0
    assert o == '10.0.0.9 bar.com\n'
    socketclass_mock.assert_called_once()
    sock.settimeout.assert_called_once()
    sock.sendto.assert_called_once()
    sock.recvfrom.assert_called_once()
    dbfile_mock.return_value.write.assert_has_calls([
        mock.call('10.0.0.9 bar.com\n'),
    ])

    # Invalidate an unexistance hostname
    dbfile_mock.reset_mock()
    socketclass_mock.reset_mock()
    sock = socketclass_mock.return_value
    sock.recvfrom.return_value = b'\x02baz.com', ('10.0.0.7', 5333)
    s, o, e = resolvecli('baz.com', '--forceresolve')
    assert e == ''
    assert s == 0
    assert o == '10.0.0.7 baz.com\n'
    socketclass_mock.assert_called_once()
    sock.settimeout.assert_called_once()
    sock.sendto.assert_called_once()
    sock.recvfrom.assert_called_once()
    dbfile_mock.return_value.write.assert_has_calls([
        mock.call('10.0.0.3 bar.com\n'),
        mock.call('10.0.0.7 baz.com\n'),
    ])


def test_cli_resolve_bad_cachefile(socketclass_mock, badfile_mock, resolvecli):
    s, o, e = resolvecli('foo.com')
    assert e.startswith('Invalid input file: ')
    assert o == ''
    assert s == 4


def test_cli_resolve_timeout(socketclass_mock, resolvecli):
    sock = socketclass_mock.return_value

    # timeout
    sock.recvfrom.side_effect = socket.timeout
    s, o, e = resolvecli('h.', '-t 8')
    assert e == 'Timeout reached.\n'
    assert s == 2

    # ctrl+c
    sock.recvfrom.side_effect = KeyboardInterrupt
    s, o, e = resolvecli('h.')
    assert e == 'Terminated by user.\n'
    assert s == 3


if __name__ == '__main__':
    from uns.cli import UNS
    UNS.quickstart(['resolve', 'foo.com'])
