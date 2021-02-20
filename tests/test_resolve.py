import socket
from unittest import mock

import pytest

from uns.protocol import resolve


def test_resolve(socketclass_mock):
    resolve('foo.com', 1)
    socketclass_mock.assert_called_once()
    sock = socketclass_mock.return_value
    sock.settimeout.assert_called_once_with(1)
    sock.sendto.assert_called_once_with(b'\x01foo.com', mock.ANY)
    sock.recvfrom.assert_called_once()

    # timeout
    sock.recvfrom.side_effect = socket.timeout
    with pytest.raises(socket.timeout):
        resolve('foo.com', 1)
