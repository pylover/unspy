from unittest import mock

from uns import resolve


def test_resolve(sockclass):
    resolve('foo.com', 1)
    sockclass.assert_called_once()
    sock = sockclass.return_value
    sock.settimeout.assert_called_once_with(1)
    sock.sendto.assert_called_once_with(b'\x01foo.com', mock.ANY)
    sock.recvfrom.assert_called_once()

# TODO: Coverage
# Github actions
