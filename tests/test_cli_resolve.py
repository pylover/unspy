import functools

from unittest import mock

cachefile = '''
#commented line

 this is another way to comment a line

10.0.0.3 bar.com
'''


def test_cli_resolve_cache(socketclass_mock, cliapp):
    resolvecli = functools.partial(cliapp, 'resolve')

    openmock = mock.mock_open(read_data=cachefile)
    with mock.patch('uns.cache.open', openmock), \
            mock.patch('os.path.exists') as existsmock:
        existsmock.return_value = True

        s, o, e = resolvecli('bar.com')
        assert e == ''
        assert s == 0
        assert o == '10.0.0.3 bar.com [cache]\n'
        socketclass_mock.assert_not_called()
        sock = socketclass_mock.return_value
        sock.settimeout.assert_not_called()
        sock.sendto.assert_not_called()
        sock.recvfrom.assert_not_called()
        openmock.return_value.write.assert_called_with('10.0.0.3 bar.com\n')

        openmock.reset_mock()
        s, o, e = resolvecli('foo.com')
        assert e == ''
        assert s == 0
        assert o == '10.0.0.2 foo.com\n'
        socketclass_mock.assert_called_once()
        sock = socketclass_mock.return_value
        sock.settimeout.assert_not_called()
        sock.sendto.assert_called_once_with(b'\x01foo.com', mock.ANY)
        sock.recvfrom.assert_called_once()
        openmock.return_value.write.assert_has_calls([
            mock.call('10.0.0.3 bar.com\n'),
            mock.call('10.0.0.2 foo.com\n'),
        ])

    # When file is invalid
    openmock = mock.mock_open(read_data='MalformedLine')
    with mock.patch('uns.cache.open', openmock), \
            mock.patch('os.path.exists') as existsmock:
        existsmock.return_value = True
        s, o, e = resolvecli('foo.com')
        assert s == 1
        assert o == ''
        assert e == 'Cannot parse: MalformedLine\n'


def test_cli_resolve_nocache(socketclass_mock, cliapp):
    nocache = functools.partial(cliapp, 'resolve', '--nocache')

    s, o, e = nocache('foo.com')
    assert e == ''
    assert s == 0
    assert o == '10.0.0.2 foo.com\n'
    socketclass_mock.assert_called_once()
    sock = socketclass_mock.return_value
    sock.settimeout.assert_not_called()
    sock.sendto.assert_called_once_with(b'\x01foo.com', mock.ANY)
    sock.recvfrom.assert_called_once()

    # Missing argument
    s, o, e = nocache()
    assert e.startswith('usage: uns resolve [-h]')
    assert s == 1
    assert o == ''

    # Short result
    s, o, e = nocache('--short', 'foo.com')
    assert s == 0
    assert o == '10.0.0.2\n'


if __name__ == '__main__':
    from uns.cli import UNS
    UNS.quickstart(['resolve', 'foo.com'])
