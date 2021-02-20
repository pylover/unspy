from unittest import mock

import pytest


@pytest.fixture
def sockclass():
    with mock.patch('socket.socket') as m:
        s = m.return_value
        s.recvfrom.return_value = b'\x02foo.com', ('10.0.0.2', 5333)
        yield m
