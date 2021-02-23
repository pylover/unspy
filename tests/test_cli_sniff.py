import socket
from unittest import mock


def test_cli_sniff(socketclass_mock, sniffcli):
    sock = socketclass_mock.return_value
    sock.recvfrom.side_effect = [
        (b'\x01foo.com', ('10.0.0.2', 5333)),
        (b'\x01bar.com', ('10.0.0.2', 5333)),
        (b'\x01foo.com', ('10.0.0.1', 3333)),
    ]

    s, o, e = sniffcli()
    assert o == '''Listening to 224.0.0.70:5333
10.0.0.2:5333 discover foo.com
10.0.0.2:5333 discover bar.com
10.0.0.1:3333 discover foo.com
'''
    socketclass_mock.assert_called_once()
    sock = socketclass_mock.return_value
    sock.settimeout.assert_not_called()
    sock.setsockopt.assert_any_call(
        socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mock.ANY)

    # ctrl+c
    sock.recvfrom.side_effect = KeyboardInterrupt
    s, o, e = sniffcli()
    assert s == 3
    assert e == 'Terminated by user.\n'
