from unittest import mock

# uns http get home.nodemcu/foo
# uns http set home.nodemcu 1
# uns http set home.nodemcu foo=bar baz="qux quux"
# uns http set home.nodemcu foo=@bar.ext


def test_http_get(socketclass_mock, requests_mock, dbfile_mock, httpcli):
    s, o, e = httpcli('get', 'foo.com')
    assert e == ''
    assert o == 'bar'
    assert s == 0
    socketclass_mock.assert_called_once()
    sock = socketclass_mock.return_value
    sock.settimeout.assert_called_once()
    sock.sendto.assert_called_once_with(b'\x01foo.com', mock.ANY)
    sock.recvfrom.assert_called_once()
    requests_mock.assert_called_with('GET', 'http://10.0.0.2', headers={})

    s, o, e = httpcli('get', 'foo.com/bar')
    assert s == 0
    requests_mock.assert_called_with('GET', 'http://10.0.0.2/bar', headers={})

    s, o, e = httpcli('set', 'foo.com', '1')
    assert s == 0
    requests_mock.assert_called_with(
        'SET', 'http://10.0.0.2',
        headers={},
        data='1'
    )

    s, o, e = httpcli('set', 'foo.com', 'bar=baz', '?qux=quux')
    assert s == 0
    requests_mock.assert_called_with(
        'SET', 'http://10.0.0.2',
        headers={},
        data=[('bar', 'baz')],
        params=[('qux', 'quux')]
    )
