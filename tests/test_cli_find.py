import socket
from unittest import mock


cachefile = '''\
10.0.0.1 h.foo
10.0.0.6 h.qux
'''


def test_cli_find(socketclass_mock, findcli):
    openmock = mock.mock_open(read_data=cachefile)
    with mock.patch('uns.cache.open', openmock), \
            mock.patch('os.path.exists') as existsmock:
        existsmock.return_value = True

        sock = socketclass_mock.return_value
        sock.recvfrom.side_effect = [
            (b'\x02h.foo', ('10.0.0.1', 5333)),
            (b'\x02h.bar', ('10.0.0.2', 5333)),
            (b'\x02h.baz', ('10.0.0.3', 3333)),
        ]

        s, o, e = findcli('h.')
        assert o == '''\
10.0.0.1 h.foo [cache]
10.0.0.6 h.qux [cache]
10.0.0.1 h.foo
10.0.0.2 h.bar
10.0.0.3 h.baz
'''
        socketclass_mock.assert_called_once()
        sock = socketclass_mock.return_value
        sock.settimeout.assert_called_with(5)

        # timeout
        sock.recvfrom.side_effect = socket.timeout
        s, o, e = findcli('h.')
        assert s == 2
        assert e == 'Timeout reached: 5.\n'

        # ctrl+c
        sock.recvfrom.side_effect = KeyboardInterrupt
        s, o, e = findcli('h.')
        assert s == 3
        assert e == 'Terminated by user.\n'
