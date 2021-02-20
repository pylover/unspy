from unittest import mock


def test_cli_resolve(socketclass_mock, cliapp):
    s, o, e = cliapp('resolve', 'foo.com')
    assert e == ''
    assert s == 0
    assert o == '10.0.0.2 foo.com\n'
    socketclass_mock.assert_called_once()
    sock = socketclass_mock.return_value
    sock.settimeout.assert_not_called()
    sock.sendto.assert_called_once_with(b'\x01foo.com', mock.ANY)
    sock.recvfrom.assert_called_once()

    # Missing argument
    s, o, e = cliapp('resolve')
    assert e.startswith('usage: uns resolve [-h]')
    assert s == 1
    assert o == ''

    # Short result
    s, o, e = cliapp('resolve', '-s', 'foo.com')
    assert s == 0
    assert o == '10.0.0.2\n'


if __name__ == '__main__':
    from uns.cli import UNS
    UNS.quickstart(['resolve', 'foo.com'])
